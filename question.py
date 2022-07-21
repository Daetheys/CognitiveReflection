import copy

class Question:
    def __init__(self,prompt,answers,keywords=None,info=None):
        self.prompt = prompt
        self.answers = answers
        self.keywords = keywords
        if keywords is None:
            self.keywords = []
        self.info = info
        if info is None:
            self.info = {}

        self.prompt_mode = 'full'
        self.nb_answers = 4
        self.qa = False
        self.answer_model='([letter]). [answer]'

    def setup(self,prompt_mode='full',nb_answers=4,answer_model='([letter]). [answer]\n',qa=False,backslash=False):

        assert prompt_mode in ['full','half','vanilla']
        self.prompt_mode = prompt_mode
        self.nb_answers = nb_answers
        self.answer_model = answer_model
        self.qa = qa
        self.backslash = backslash

    def serialize(self):
        return {"prompt":self.prompt,
                "answers":self.answers,
                "keywords":self.keywords,
                "info":self.info}

    def __str__(self):
        s = ''
        if self.qa:
            s += 'Q:'
        s += str(self.prompt)
        if self.prompt_mode == 'half':
            ls = s.split(' ')
            s2 = ""
            for si in ls[:len(ls)//2]:
                s2 += si+" "
            s = s2[:-1]
        if self.prompt_mode == 'full':
            for i in range(min(self.nb_answers,len(self.answers))):
                s2 = copy.copy(self.answer_model)
                s2 = s2.replace('[letter]',chr(97+i))
                s2 = s2.replace('[number]',str(i+1))
                s2 = s2.replace('[answer]',self.answers[i])
                s += s2
            if self.backslash:
                s += "\n\n"
        if self.qa:
            s += "A:"
        return s

    def __repr__(self):
        return str(self)
