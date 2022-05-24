import os

from module import Module
from question import Question

class Dataset(Module):
    def __init__(self,config):
        super().__init__(config)

        self.load()

    @property
    def path(self):
        return self.config['data_path']

    def load(self):
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
