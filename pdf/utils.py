import pdfplumber
import re

PATTERN_1 = r'\nQuestion ?\d+'
PATTERN_2 = r'\nPhrase ?\d+ ?:\nA'
PATTERN_3 = r'\nPhrase ?\d+\nA'

TEXT_TITLE = r'Texte ?\d+ ?'
COLON = r':'
NEWLINE = r'\n'

MIN_LENGTH = 5

class Pdf:
    def __init__(self, file_path='pdf/tef_textes.pdf'):
        self.questions = {}
        self.count = 0
        self.patterns = set((PATTERN_1, PATTERN_2, PATTERN_3))
        self.pages = self.__load(file_path)
        questions, count = self.find_in_pages(self.pages, self.patterns)
        self.questions = questions
        self.count = count

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
                #first \n = end of title.
                #newline = re.search(NEWLINE, text)
                title = text[2: newline.start()]
                body = text[newline.end(): question.start() if question else question]
                
                #print(page, colored(title, 'green'))
            elif texte.start() == 0: #TITLE BEGINS AFTER FIRST COLON
                    if newline.start() - texte.end() < MIN_LENGTH:
                        #print(colored('CONDITION ' + page, 'blue'))
                        newline = re.search(NEWLINE, text[newline.end():])
                    title =text[colon.start()+2: newline.start()]
                    body = text[texte.end(): question.start() if question else question]

                    #print(page, colored(title, 'green'))
            else:
                # Title is from beginning of text to Texte
                title = text[0:texte.start()]
                #print(page, colored(title, 'yellow'))
                body = text[texte.end(): question.start() if question else question]


            pages[page] = {'title': title, 'body': body, 'questions': text[question.start():] if question else ''}
        return pages



    def __repr__(self):
        return f'<Pdf Object: Pg {len(self.pages)}, Qstn {self.count}>'
    
if __name__ == '__main__':
    print('loading...')
    pdf = Pdf()
    print(pdf.find_content())


# Logic
# If text has : at the beginning, then Title starts here. ends when we see 'Texte'
#     body starts from end of texte to question.
# If text begins with the word Texte, then Title starts after : and ends after \n
#     body begins from end of title to question.


