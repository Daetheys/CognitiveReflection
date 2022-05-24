class Module:
    def __init__(self, config):
        self.config = config

    @property
    def name(self):
        return self.config['name']
