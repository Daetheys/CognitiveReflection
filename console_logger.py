import xlsxwriter
import os
import traceback

from module import Module
import json

class ConsoleLogger(Module):
    def __init__(self,config):
        super().__init__(config)
                    
    def log(self,*args):
        #Only logs str
        s = ""
        for a in args:
            if isinstance(a,str):
                s += a
            elif isinstance(a,float):
                s += str(a)
            elif isinstance(a,int):
                s += str(a)
            s += " "
        print(s)
        #Writes the str
        self.f.write(s+"\n")

    def __enter__(self):
        self.f = open(os.path.join(self.path,'log.txt'),'a')
        return self

    def __exit__(self,exc_type, exc_value, tb):
        #Close the file
        self.f.close()

        #Write the config
        f = open(os.path.join(self.path,'config.json'),'w')
        json.dump(self.config.to_dict(),f)

        #Print the exception if one occurs
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        return False
        
class XLSXLogger(ConsoleLogger):
    def __init__(self,config):
        super().__init__(config)

        self.wb = xlsxwriter.Workbook(os.path.join(self.path,'results.xlsx'))
        self.ws = self.wb.add_worksheet()

        self.bold = self.wb.add_format({'bold':True})
        
        self.to_save = {}

    def log(self,*args,x=None,y=None):
        #Log in the txt file
        super().log(*args)
        #Log for xlsx
        if not(x is None) and not(y is None):
            self.to_save[(x,y)] = args

    def __enter__(self):
        return super().__enter__()
        
    def __exit__(self,*args):
        #Save XLSX
        for k in self.to_save:
            if len(self.to_save[k])>1:
                self.ws.write_rich_string(k[0],k[1],*self.to_save[k])
            else:
                self.ws.write(k[0],k[1],*self.to_save[k])
        self.wb.close()
        #Save the rest
        return super().__exit__(*args)
