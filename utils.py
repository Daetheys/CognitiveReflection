class DictOfDict(dict):
    def __getitem__(self,k):
        try:
            return super().__getitem__(k)
        except KeyError:
            d = DictOfDict()
            super().__setitem__(k,d)
            return d
