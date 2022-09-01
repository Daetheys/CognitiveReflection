import json

from module import Module
from question import Question


class Dataset(Module):
    def __init__(self, config):
        super().__init__(config)

        # List of questions
        self.questions = []

        self.f = config['file_as_string']

        self.load()

    @property
    def path(self):
        return self.config['data_path']

    def load(self):
        def add_question(stack):
            # Adds a question from the stacked informations to the list
            question = Question(stack[0], stack[1:])
            self.questions.append(question)

        questions = json.load(self.f)
        for q in questions:
            self.questions.append(
                Question(
                    prompt=q['text'],
                    title=q['title'],
                    id=q['id']
                )
            )

    def __iter__(self):
        return iter(self.questions)

    def __len__(self):
        return len(self.questions)
