import os
import json
import traceback

from module import Module

class Dict:
    def __init__(self,d=None):
        if d is None:
            d = {}
        self.d = d

    def __setitem__(self,k,v):
        self.d[k] = v

    def __getitem__(self,k):
        try:
            return self.d[k]
        except KeyError:
            self.d[k] = Dict()
            return self.d[k]

    def to_dict(self):
        d = {}
        for k in self.d:
            if hasattr(self.d[k],'to_dict'):
                d[k] = self.d[k].to_dict()
            else:
                d[k] = self.d[k]
        return d


class JSONLogger(Module):
    def __init__(self,config):
        super().__init__(config)
        self.d = Dict()

    def serialize(self):
        return self.d.to_dict()

    @property
    def path(self):
        return os.path.join('TRAININGS',self.name)
        
    @property
    def log(self):
        return self.d
        
    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_value, tb):
        #Write the file
        f = open(os.path.join(self.path,'data.json'),'a')
        json.dump(self.serialize(),f)
        f.close()

        #Print the exception if one occurs
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        return False
