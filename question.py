class Question:
    def __init__(self,prompt,answers):
        self.prompt = prompt
        self.answers = answers

        self.prompt_mode = 'full'
        self.nb_answers = 4

    def setup(self,prompt_mode='full',nb_answers=4):

        assert prompt_mode in ['full','half']
        self.prompt_mode = prompt_mode
        self.nb_answers = nb_answers

    def __str__(self):
        s = str(self.prompt)
        if self.prompt_mode == 'half':
            ls = s.split(' ')
            s2 = ""
            for si in ls[:len(ls)//2]:
                s2 += si+" "
            s = s2[:-1]
        if self.prompt_mode == 'full':
            for i in range(min(self.nb_answers,len(self.answers))):
                s += '\n'+self.answers[i]
            s += "\n"
        return s

    def __repr__(self):
        return str(self)
