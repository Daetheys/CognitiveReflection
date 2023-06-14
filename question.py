class Question:
    def __init__(self, prompt, answers=None, id=None, title=None):
        self.prompt = prompt
        self.answers = answers
        self.title = title
        self.id = id 
        self.prompt_mode = 'full'
        self.nb_answers = 4

    def setup(self, prompt_mode='full', nb_answers=4):

        # check prompt_mode is a valid value
        assert prompt_mode in ['full', 'half']
        # set prompt_mode as a class variable
        self.prompt_mode = prompt_mode
        # set nb_answers as a class variable
        self.nb_answers = nb_answers

    def serialize(self):
        return {"prompt":self.prompt,
                "answers":self.answers}
                # "keywords":self.keywords}

    def __str__(self):
        s = str(self.prompt)
        if self.prompt_mode == 'half':
            ls = s.split(' ')
            s2 = ""
            for si in ls[:len(ls)//2]:
                s2 += si+" "
            s = s2[:-1]
        if self.prompt_mode == 'full':
            if self.answers is not None:
                for i in range(min(self.nb_answers, len(self.answers))):
                    s += '\n'+self.answers[i]
            s += "\n"

        return s

    def __repr__(self):
        return str(self)
