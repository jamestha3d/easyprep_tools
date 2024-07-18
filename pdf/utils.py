import pdfplumber
import re

PATTERN_1 = r'\nQuestion ?\d+'
PATTERN_2 = r'\nPhrase ?\d+ ?:\nA'
PATTERN_3 = r'\nPhrase ?\d+\nA'


PHRASE_PATTERN_1 = r'\nPhrase ?\d+ ?:'
PHRASE_PATTERN_2 = r'\nPhrase ?\d+'

TEXT_TITLE = r'Texte ?\d+ ?'
COLON = r':'
NEWLINE = r'\n'

MIN_LENGTH = 5

# OPTION_A = r'\nA.?'
# OPTION_B = r'\nB.?'
# OPTION_C = r'\nC.?'
# OPTION_D = r'\nD.?'

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

    def group_patterns(self):
        pages = self.find_content()
        all_questions = {}
        for num, page in pages.items():
            
            all_questions[num] = {}
            questions = page['questions']
            offset = 0
            while True:
                question_title = Pdf.find_first_pattern(questions, self.patterns2)
                
                if question_title:
                    # print('question title', str(question_title.group(0)), end='###')
                    q_start = question_title.end()
                    # print('question start', q_start, end='###')
                    next_title = Pdf.find_first_pattern(questions[q_start:], self.patterns2)
                    if next_title:
                        # print('next title', str(next_title.group(0)), end='###')
                        q_end = next_title.start()
                        # print('question_end', q_end, end='###')
                        question_body = questions[q_start:q_start+q_end] 
                        all_questions[num][question_title.group(0)] = question_body
                        questions = questions[q_end:]
                        
                    else:
                        question_body = questions[q_start:]
                        all_questions[num][question_title.group(0)] = question_body
                        break

                else:
                    # print('finished', end='###')
                    break
            
        return all_questions
    

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
                    # print('question title', str(question_title.group(0)), end='###')
                    q_start = question_title.end()
                    # print('question start', q_start, end='###')
                    next_title = Pdf.find_first_pattern(questions[q_start:], self.patterns2)
                    if next_title:
                        # print('next title', str(next_title.group(0)), end='###')
                        q_end = next_title.start()
                        # print('question_end', q_end, end='###')
                        question_body = questions[q_start:q_start+q_end] 
                        all_questions[num][question_title.group(0)] = question_body
                        questions = questions[q_end:]
                        
                    else:
                        question_body = questions[q_start:]
                        all_questions[num][question_title.group(0)] = question_body
                        break

                else:
                    # print('finished', end='###')
                    break
            
        return all_questions

    def group_options(self):
        all_questions = self.group_questions()
        all_options = {}
        for page, questions in all_questions.items():
            all_options[page] = {}
            for title, question in questions.items():
                all_options[page][title]={} #we should separate title and add first body with title
                options = question
                while True:
                    first_option = Pdf.find_first_pattern(options, self.option_patterns)
                    
                    if first_option:
                        # print('question title', str(first_option.group(0)), end='###')
                        o_start = first_option.end()
                        # print('question start', o_start, end='###')
                        next_option = Pdf.find_first_pattern(options[o_start:], self.option_patterns)
                        if next_option:
                            # print('next title', str(next_option.group(0)), end='###')
                            o_end = next_option.start()
                            # print('question_end', o_end, end='###')
                            option_body = options[o_start:o_start+o_end] 
                            all_options[page][title][first_option.group(0)] = option_body
                            options = options[o_end:]
                            
                        else:
                            option_body = options[o_start:]
                            all_options[page][title][first_option.group(0)] = option_body
                            break

                    else:
                        # print('finished', end='###')
                        break

        return all_options

    def __repr__(self):
        return f'<Pdf Object: Pg {len(self.pages)}, Qstn {self.count}>'
    
if __name__ == '__main__':
    print('loading...')
    pdf = Pdf()
    q = pdf.group_questions()
    print(pdf.find_content())


# Logic
# If text has : at the beginning, then Title starts here. ends when we see 'Texte'
#     body starts from end of texte to question.
# If text begins with the word Texte, then Title starts after : and ends after \n
#     body begins from end of title to question.



# question title 
# Question 24###question start 12###next title 
# Question 25###question_end 170###question title 
# Question 25###question start 24###next title 
# Question 26###question_end 170###question title 
# Question 26###question start 36###next title 
# Question27###question_end 250###question title 
# Question27###question start 47###
# question title 
# Question 6###question start 11###next title 
# Question 7###question_end 228###question title 
# Question 7###question start 22###next title 
# Question 8###question_end 167###question title 
# Question 8###question start 33###
# question title 