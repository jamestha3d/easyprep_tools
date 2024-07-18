from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.db import transaction, models
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
import xlwt
import csv
import uuid
import datetime


class ExportData:

    renamed_fields = {
        "nme": "Name",
        "Usr": "User",
        "Ordr": "Order",
    }   

    default_excluded_fields = ["guid_id", "assessmentdatetime"]

    content_types = {
        "txt": "text/plain",
        "csv": "text/csv",
        "xls": "application/vnd.ms-excel",
        "json": "application/json",
        "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    def __init__(self, queryset, selected=None, exclude=None, path=None, filename=None):
        if type(queryset) != dict:
            raise Exception('Queryset must be a dict instance')
        self.queryset = []
        self.sheets = []
        self.models = {}
        for sheet_name, data in queryset.items():
            if hasattr(data, 'model'):
                model = data.model
            elif isinstance(data, list):
                model = data[0].__class__ #type(data[0])
            else:
                raise Exception('must be queryset or list')
            model_name = model.__name__
            self.queryset.append(data)
            self.sheets.append((sheet_name, model_name))
            if model_name in self.models:
                continue
            if type(model) == ModelBase:
                fields = [field.name for field in model._meta.fields if field.name not in self.default_excluded_fields]
            else:
                fields = [attr for attr,_ in data[0].__dict__.items() if not self.is_private_attr(attr) and attr not in self.default_excluded_fields]
            self.models[model_name] = fields
        
        if exclude:
            self.default_excluded_fields.extend(exclude)
        
        self.get_fields(selected)
        self.get_column_names()
        self.filename = filename

    def get_fields(self, selected):
        #selected should be a dictionary with the sheetnames and fields to write.
        if selected:
            if type(selected) != dict:
                raise Exception('selected must be a dict instance with key of sheetname and values containing an iterable of fields to write')
            
            for model_name,fields in selected.items():
                if model_name in self.models:
                    selected_fields = [field for field in fields if field in self.models[model_name]]
                    self.models[model_name] = selected_fields
    
    def get_column_names(self):
        # #column names for fields that will be written to the excel sheet
        column_names = {}
        for model, fields in self.models.items():
            field_list = [self.renamed_fields[field] if field in self.renamed_fields else field.capitalize() for field in fields]
            column_names[model] = field_list
        self.column_names = column_names

    def get_formatted_response(self, format):
        response = HttpResponse(content_type=self.content_types[format])
        filename = f'ResearchData{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
        response['Content-Disposition'] = f'attachment; filename="{self.filename or filename}.{format}"'
        return response
    
    def parse_int(self, string):
        if isinstance(string, int) or isinstance(string, float):
            return string
        else:
            return str(string)

    def excel_writer(self):
        wb = xlwt.Workbook(encoding='utf-8')

        for sheet in range(len(self.queryset)):
            #add sheet
            model_name = self.sheets[sheet][1]
            #column_names = self.column_names[model_name]
            column_names = self.models[model_name]
            #column_names = self.column_names[sheet][1]
            ws = wb.add_sheet(f'{self.sheets[sheet][0]}') #

            #sheet header, first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            
            #write column names
            for col_num in range(len(column_names)):
                ws.write(row_num, col_num, str(column_names[col_num]), font_style) #start at 0 row 0 column

            #sheetbody remaining rows
            font_style = xlwt.XFStyle()
            rows = self.get_values_list(sheet) #
            for row in rows:
                row_num += 1
                for col_num in range(len(row)):
                    #cast to str incase of UUID
                    ws.write(row_num, col_num, self.parse_int(row[col_num]), font_style)
        return wb
    
    def export_as_excel(self, path=None):
        file = self.excel_writer()
        if path:
            file.save(path)
            print(f'file saved to {path}')
            return
        response = self.get_formatted_response('xls')
        file.save(response)
        return response
        
    def export_as_format(self, format):
        if format not in self.content_types:
            format = "csv"
        
        if format == "csv":
            return self.export_as_csv()
        elif format == "xls":
            return self.export_as_excel()
        
    def get_values_list(self, sheet=None):
        def get_sheet_values(sheet):
            if isinstance(self.queryset[sheet], QuerySet):
                model_name = self.sheets[sheet][1]
                return self.queryset[sheet].values_list(*self.models[model_name])
            else:
                values_list = []
                for item in self.queryset[sheet]:
                    if item is not None:
                        item_list = []
                        for attr,val in item.__dict__.items():
                            if not self.is_private_attr(attr):
                                item_list.append(val)
                        values_list.append(item_list)
                return values_list
            
        if sheet is not None:
            return get_sheet_values(sheet)
        else:
            #csv file, concatenate all values.
            values_list = []
            for sheet in range(len(self.queryset)):
                values_list.extend(get_sheet_values(sheet))
            return values_list
        
    def is_private_attr(self, attr):
        return attr[0] == '_'
    
    def export_as_csv(self, path=None):
        if path:
            with open(path, 'w', newline='') as csv_file:
                self.csv_writer(csv_file)
                print(f'file saved to {path}')
            return
        response = self.get_formatted_response('csv')
        self.csv_writer(response)
        return response

    def csv_writer(self, file):
        if len(self.models) != 1:
            raise Exception('cannot export multiple models to csv. use xls')
        column_names = list(self.column_names.values())[0]
        writer = csv.writer(file)
        writer.writerow(column_names)
        csv_content = self.get_values_list()
        for row in csv_content:
            writer.writerow(row)
    

class ImportExcelData:
    failed_keys = {}
    current_sheet = None
    guids = {}
    cache = {}
    def __init__(self, path, replace_guids = False):
        sheets = pd.read_excel(path, sheet_name=None)
        for sheet_name, df in sheets.items():
            sheets[sheet_name] = df.fillna('') #replace Nan with empty string
            if 'guid' in df.columns and replace_guids:
                sheets[sheet_name]['guid'] = sheets[sheet_name]['guid'].apply(self.replace_guid)
        self.sheets = sheets


    models = {} #define models. {'model_name': model_class}
        
    def load_to_db(self):
        with transaction.atomic():
            for sheet_name, df in self.sheets.items():
                num_rows = df.shape[0]
                
                print(f"Loading {sheet_name}...")
                self.current_sheet = sheet_name
                if sheet_name in self.models:
                    model = self.models[sheet_name]
                    items = []
                    for index, row in df.iterrows():
                        if index % 100 == 0:
                            print(f'\nloading item {index + 1}/{num_rows}')
                        row_dict = row.to_dict()
                        rows = self.get_valid_rows(row_dict)
                        rows = self.deserialize(model, rows)
                        item = model(**rows)
                        # if model == Model_to_be_renamed: #rename instance if exists
                        #     while Model_to_be_rename.objects.filter(name=item.name).exists():
                        #         item.name = item.name + ' - Copy'
                        items.append(item)
                        #model.objects.create(**rows)
                    print("bulk creating items...")
                    model.objects.bulk_create(items)
                    print('updating foreign keys', sheet_name)
                    self.update_foreign_keys(model, sheet_name)
    
    def deserialize(self, model, data):
        deserialized_json = {}
        for field_name, field_value in data.items():
            field = model._meta.get_field(field_name)
            if isinstance(field, models.ManyToManyField):
                related_model = field.related_model
                related_instances = related_model.objects.filter(pk__in=field_value)
                deserialized_json[field_name] = related_instances
            elif isinstance(field, models.ForeignKey):
                related_model = field.related_model
                try:
                    related_instance = self.get_cache_obj(related_model, field_value)
                    deserialized_json[field_name] = related_instance
                except related_model.DoesNotExist:
                    deserialized_json[field_name] = None #this object might not have been created yet so let's make it None for now.
                    print('@', end='')
                    self.register_failed_key(field.name, field_value) #save this info so that we can update this object later
            elif isinstance(field, models.IntegerField):
                deserialized_json[field_name] =int(field_value)
            elif isinstance(field, models.BooleanField):
                deserialized_json[field_name] = True if field_value == 'True' else False
            elif isinstance(field, models.UUIDField):
                deserialized_json[field_name] = uuid.UUID(field_value)
            else:
                deserialized_json[field_name] = field_value
        return deserialized_json

    def register_failed_key(self, field_name, value):
        current_sheet = self.current_sheet
        if current_sheet:
            if current_sheet in self.failed_keys:
                if field_name in self.failed_keys[current_sheet]:
                    self.failed_keys[current_sheet][field_name].append(value)
                else:
                    self.failed_keys[current_sheet][field_name] = [value]
            else:
                self.failed_keys[current_sheet] = {field_name: [value]}

    def update_foreign_keys(self, model, sheet_name):
        '''
        This is to update self referential foreign keys, as the objects might not have been created at the point of calling load_to_db
        '''
        if sheet_name not in self.failed_keys:
            return
        fields = list(self.failed_keys[sheet_name].keys())
        values = []
        for field in fields:
            values.extend(self.failed_keys[sheet_name][field])
        model_fields = model._meta.get_fields()
        if fields:
            model_fields = [field for field in model_fields if field.name in fields]
        foreign_keys = [field for field in model_fields if isinstance(field, models.ForeignKey)]
        df = self.sheets[sheet_name]
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            rows = self.get_valid_rows(row_dict)
            guid = rows.get('guid')
            for field in foreign_keys:
                related_model = field.related_model
                field_value=rows.get(field.name)
                if field_value is not None and field_value in values:
                    try:
                        instance = model.objects.get(guid=guid) #object should exist we just created it
                    except ObjectDoesNotExist:
                        continue
                    try:
                        related_instance  = self.get_cache_obj(related_model, field_value)
                        setattr(instance, field.name, related_instance)
                        print(f"Updating {instance}'s {field.name} with {related_instance}")
                        instance.save()
                    except related_model.DoesNotExist:
                        print('Object does not exist', field.name, field_value, guid)

    def get_valid_rows(self, rows):
        valid_rows = {field: self.guids[value] if value in self.guids else value for field, value in rows.items() if value != 'None'}

        return valid_rows
    
    def replace_guid(self, string):
        try:
            g = uuid.UUID(string)
            if string in self.guids:
                #we've seen this guid before.
                return self.guids[string]
            else:
                #seeing this guid for the first time. generate new guid and hash it
                new_guid = str(uuid.uuid4())
                self.guids[string] = new_guid
                return new_guid
        except:
            return string
        
    def get_cache_obj(self, model, guid):
        model_name = model.__name__
        if model_name not in self.cache:
            self.cache[model_name] = {}
        elif guid in self.cache[model_name]:
            obj = self.cache[model_name][guid]
            print('#', end='')
            return obj
        
        obj = model.objects.get(pk=guid)
        print('.', end='')
        self.cache[model_name][guid] = obj
        return obj
    
