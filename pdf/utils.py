import pdfplumber
import re
import json

PATTERN_1 = r'\nQuestion ?\d+'
PATTERN_2 = r'\nPhrase ?\d+ ?:\nA'
PATTERN_3 = r'\nPhrase ?\d+\nA'


PHRASE_PATTERN_1 = r'\nPhrase ?\d+ ?:'
PHRASE_PATTERN_2 = r'\nPhrase ?\d+'

TEXT_TITLE = r'Texte ?\d+ ?'
COLON = r':'
NEWLINE = r'\n'

MIN_LENGTH = 5

OPTION_A = r'\nA(?:[.)]?)'
OPTION_B = r'\nB(?:[.)]?)'
OPTION_C = r'\nC(?:[.)]?)'
OPTION_D = r'\nD(?:[.)]?)'

class Pdf:
    def __init__(self, file_path='pdf/tef_textes.pdf'):
        self.questions = {}
        self.count = 0
        self.patterns = set((PATTERN_1, PATTERN_2, PATTERN_3))
        self.patterns2 = set((PATTERN_1, PHRASE_PATTERN_1, PHRASE_PATTERN_2))
        self.pages = self.__load(file_path)
        questions, count = self.find_in_pages(self.pages, self.patterns)
        self.questions = questions
        self.count = count
        self.option_patterns = [OPTION_A, OPTION_B, OPTION_C, OPTION_D]

    def __load(self, file_path):
        text = {}
        with pdfplumber.open(file_path) as pdf:
            for index, page in enumerate(pdf.pages):
                text[f"{index+1}"] = page.extract_text()
        return text
    
    @staticmethod
    def find_pattern(text:str, pattern):
        matches = re.findall(pattern, text)
        return matches
    
    @staticmethod
    def find_patterns(text:str, patterns):
        matches = []
        for pattern in patterns:
            match = Pdf.find_pattern(text, pattern)
            matches+=match
        return matches
    
    @staticmethod
    def find_first_pattern(text:str, patterns):
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match
    
    @staticmethod
    def find_in_pages(pages:dict, patterns:list, empty=True):
        count = 0
        questions = {}
        for page, text in pages.items():
            matches = Pdf.find_patterns(text, patterns)
            count += len(matches)
            if empty:
                questions[page] = matches
            else:
                if matches:
                    questions[page] = matches

        print(f'{count} questions found')
        return questions, count

    def find_texts(self, text):
        begin_match = re.search(TEXT_TITLE, text)
        if begin_match:
            start_position = begin_match.end()
        end_match = re.search(PATTERN_1, text[start_position:])

    def show(self, n=80):
        for page,text in self.pages.items():
            first_n = text[:n].replace('\n', '\\n')
            match = bool(re.search(TEXT_TITLE, first_n)) #'Texte' in first_n
            print(page, first_n, match)

    def find_content(self):
        pages = {}
        
        for page, text in self.pages.items():
            colon = re.search(COLON, text)
            newline = re.search(NEWLINE, text)
            texte = re.search(TEXT_TITLE, text)
            question = self.find_first_pattern(text, self.patterns)
            if colon.start() == 0: #COLON is at beginning of text
                title = text[2: newline.start()]
                body = text[newline.end(): question.start() if question else question]
                
                
            elif texte.start() == 0: #TITLE BEGINS AFTER FIRST COLON
                    if newline.start() - texte.end() < MIN_LENGTH:
                        newline = re.search(NEWLINE, text[newline.end():])
                    title =text[colon.start()+2: newline.start()]
                    body = text[texte.end(): question.start() if question else question]

                   
            else:
                # Title is from beginning of text to Texte
                title = text[0:texte.start()]
                
                body = text[texte.end(): question.start() if question else question]


            pages[page] = {'title': title, 'body': body, 'questions': text[question.start():] if question else ''}
        return pages

    def group_questions(self):
        pages = self.find_content()
        all_questions = {}
        for num, page in pages.items():
            
            all_questions[num] = {}
            questions = page['questions']
            offset = 0
            while True:
                question_title = Pdf.find_first_pattern(questions, self.patterns2)
                
                if question_title:
                    q_start = question_title.end()
                    next_title = Pdf.find_first_pattern(questions[q_start:], self.patterns2)
                    if next_title:
                        q_end = next_title.start()
                        question_body = questions[q_start:q_start+q_end] 
                        all_questions[num][question_title.group(0)] = question_body
                        questions = questions[q_end:]
                        
                    else:
                        question_body = questions[q_start:]
                        all_questions[num][question_title.group(0)] = question_body
                        break

                else:
                    break
            
        return all_questions
    

    def group_options(self):
        all_questions = self.group_questions()
        all_options = {}
        for page, questions in all_questions.items():
            all_options[page] = {}
            for title, question in questions.items():
                all_options[page][title]={}
                options = question
                start = True
                while True:
                    
                    first_option = Pdf.find_first_pattern(options, self.option_patterns)
                    
                    if first_option:
                        o_start = first_option.end()
                        next_option = Pdf.find_first_pattern(options[o_start:], self.option_patterns)
                        if next_option:
                            o_end = next_option.start()
                            option_body = options[o_start:o_start+o_end]
                            if start:
                                start = False
                                question_body = options[:first_option.start()]
                                all_options[page][title]['question'] = question_body
                            all_options[page][title][first_option.group(0)] = option_body
                            options = options[o_end:]
                            
                        else:
                            option_body = options[o_start:]
                            all_options[page][title][first_option.group(0)] = option_body
                            break

                    else:
                        break

        return all_options
    
    def strip_chars(self):
        all_questions = self.group_options()
        questions_copy = {}
        for page, questions in all_questions.items():
            new_page = page.strip('\n: ')
            questions_copy[new_page] = {}
            for title, question in questions.items():
                new_title = title.strip('\n: ')
                questions_copy[new_page][new_title] = {}
                for option, option_text in question.items():
                    new_option = option.strip('\n:. )')
                    questions_copy[new_page][new_title][new_option] = option_text.strip('\n: ')

        return questions_copy


    def to_json(self):
        pages = self.find_content()
        all_questions = self.strip_chars()
        questions_copy = []
        for page, questions in all_questions.items():
            question_dict = {}
            question_dict['questionGroup'] = {}
            question_dict['questionGroup']['groupTitle'] = pages[page]['title']
            question_dict['questionGroup']['groupText'] = pages[page]['body']
            question_dict['questions'] = []
            for title, question in questions.items():
                question_text = {}
                question_text['questionText'] = all_questions[page][title].get('question')
                question_text['options'] = []
                for option, option_t in question.items():
                    if option == 'question':
                        continue
                    option_text = {}
                    option_text['option'] = option
                    option_text['text'] = option_t
                    option_text['isCorrectAnswer'] = False
                    question_text['options'].append(option_text)
                question_dict['questions'].append(question_text)
            questions_copy.append(question_dict)
        return questions_copy


    def save_json(self, filename='tef_textes.json'):
        questions = self.to_json()
        dictionary = {'questions': questions}
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(dictionary, json_file, ensure_ascii=False, indent=4)
        

    def __repr__(self):
        return f'<Pdf Object: Pg {len(self.pages)}, Qstn {self.count}>'
    
if __name__ == '__main__':
    print('loading...')
    pdf = Pdf()
    q = pdf.group_questions()
    print(pdf.find_content())

#Final output should look like this
# [
#     {
        
#        "questionGroup": {
#            "title": "this is the title",
#            "instruction": "this is the instruction",
#            "other_fields": "these are the other fields"
#        }
#        "questions": [
#                {
#                    "questionText": "what is your name",
#                     "options": [
#                           {
#                                "text": "Chinedu",
#                                 "isCorrectAnswer": false
#                            }
#                      ]
#                 }
#           ]
#      }
# ]



# Logic
# If text has : at the beginning, then Title starts here. ends when we see 'Texte'
#     body starts from end of texte to question.
# If text begins with the word Texte, then Title starts after : and ends after \n
#     body begins from end of title to question.

