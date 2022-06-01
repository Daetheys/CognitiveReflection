import os

class Module:
    def __init__(self,config):
        self.config = config

    @property
    def name(self):
        return self.config['name']

    @property
    def path(self):
        return os.path.join('TRAININGS',self.name)
