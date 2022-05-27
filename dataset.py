import os
import json

from module import Module
from question import Question


class Dataset(Module):
    def __init__(self, config):
        super().__init__(config)

        # List of questions
        self.questions = []

        self.load()
       

    @property
    def path(self):
        return self.config['data_path']

    def load(self):
        def add_question(stack):
            # Adds a question from the stacked informations to the list
            question = Question(stack[0], stack[1:])
            self.questions.append(question)
        
        extension = self.config['data_path'].split('.')[-1]

        if extension == 'txt':
            stack = []
            with open(self.path, 'r') as f:
                while True:
                    line = f.readline()
                    # Empty -> end the process
                    if len(line) == 0:
                        break
                    # End of question -> store the question
                    if line == '\n':
                        add_question(stack)
                        stack = []
                    else:
                        stack.append(line[:-1])
                # Store the last question being processed
                if len(stack) != 0:
                    add_question(stack)

        elif extension == 'json':
            with open(self.path, "r") as f:
                questions = json.load(f)
                for q in questions:
                    self.questions.append(
                        Question(
                            prompt=q['text'],
                            title=q['title'],
                             id=q['id']
                        )
                    )

        else:
            raise Exception('Extension not supported')

    def __iter__(self):
        return iter(self.questions)

    def __len__(self):
        return len(self.questions)
