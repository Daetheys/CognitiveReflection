class SafeDict(dict):
    """Dictinnary for which an error is returned 
    if the user tries to assign an unknown variable
     (useful to be sure that there aren't spelling mistakes in the config parameters) """

    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def __setitem__(self, k, v):
        if self.get(k) is None:
            raise KeyError('New keys are not allowed!')
        self.update({k: v})
