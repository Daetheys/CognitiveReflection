import os
import json

from module import Module
from question import Question

class Dataset(Module):
    def __init__(self,config):
        super().__init__(config)

        self.load()

    @property
    def path(self):
        return self.config['data_path']

    def load_json(self):
        with open(self.path,'r') as f:
            data = json.load()


    def load(self):
        ext = self.path.split('.')[-1]
        if ext == 'txt':
            self.load_txt()
        elif ext == 'json':
            self.load_json()

    def load_json(self):
        with open(self.path,'r') as f:
            data = json.load(f)
        self.questions = []
        for k in data:
            q = Question(data[k]['question'],data[k]['answers'],keywords=data[k]['keywords'])
            self.questions.append(q)
    
    def load_txt(self):
        #List of questions
        self.questions = []
        def add_question(stack):
            #Adds a question from the stacked informations to the list
            question = Question(stack[0],stack[1:])
            self.questions.append(question)

        stack = []
        with open(self.path,'r') as f:
            while True:
                line = f.readline()
                #Empty -> end the process
                if len(line) == 0:
                    break
                #End of question -> store the question
                if line == '\n':
                    add_question(stack)
                    stack = []
                else:
                    stack.append(line[:-1])
            #Store the last question being processed
            if len(stack) != 0:
                add_question(stack)

    def __iter__(self):
        return iter(self.questions)

    def __len__(self):
        return len(self.questions)
