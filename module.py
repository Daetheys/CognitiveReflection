class Module:
    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return self.config['name']
    
    @property
    def exp(self):
        return self.config['exp']
