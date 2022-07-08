import json
import numpy as np
import copy

from utils import DictOfDict

class DecisionFun:
    def __init__(self):
        self.reset()
        
    def reset(self):
        pass
    
    def __call__(self,k):
        if np.random() > 0.5:
            return "A"
        return "S"

class LindaDecisionFun(DecisionFun):
    def reset(self,val=None):
        if not(val is None):
            self.choice = val
        else:
            self.choice = int(np.random.random()>0.5)

    @property
    def values(self):
        return [0,1]
        
    def __call__(self,k):
        if k == "work 1":
            return ['S','A'][1-self.choice]
        return ['S','A'][self.choice]

class BillDecisionFun(DecisionFun):
    def reset(self,val=None):
        if not(val is None):
            self.choice = val
        else:
            self.choice = int(np.random.random()>0.5)

    @property
    def values(self):
        return [0,1]
        
    def __call__(self,k):
        if k == "hobby 2":
            return ['S','A'][1-self.choice]
        return ['S','A'][self.choice]
        
class Combinator:
    def __init__(self,path_in,path_out,mode=None):
        self.path_in = path_in
        self.path_out = path_out
        self.mode = mode

        if mode is None:
            self.decision_fun = DecisionFun()
        elif mode == 'linda':
            self.decision_fun = LindaDecisionFun()
        elif mode == 'bill':
            self.decision_fun = BillDecisionFun()

    def load(self):
        with open(self.path_in,'r') as f:
            self.data = json.load(f)

    def generate_all(self):
        print('--- Generating all sentences ---')

        #Name generator
        self.name_index = 0
        def next_name():
            global index
            out = self.data['name'][self.name_index%len(self.data['name'])]
            self.name_index += 1
            return out

        #Generate next vignette
        def generate_next(s,classes,decision_fun,info):
            def update(s,k,e,info):
                s2 = copy.deepcopy(s)
                for i in range(len(s2)):
                    s2[i] = s2[i].replace("["+k+"]",e)
                info2 = info.copy()
                info2[k] = [t,e]
                return s2,info2
            if len(classes)==0:
                return [(s,info)]
            k = classes.pop()
            t = decision_fun(k)
            l = []
            if k == 'name':
                name = next_name()
                s2,info2 = update(s,k,name,info)
                l += generate_next(s2,classes,decision_fun,info2)
            else:
                for e in self.data[k][t]:
                    s2,info2 = update(s,k,e,info)
                    classes2 = copy.deepcopy(classes)
                    l += generate_next(s2,classes2,decision_fun,info2)
            return l

        #Stack all generated vignettes
        l = []
        for order in range(2): #Order of answers varies
            for v in self.decision_fun.values: #Inverse the decision settings
                #Invert the answers depending on order
                s = [self.data['question_model']]+self.data['answers_model'][::order*2-1]
                info = {}
                #Sets up the decision function with the desired setting
                classes = list(self.data.keys())
                classes.remove("question_model")
                classes.remove("answers_model")
                self.decision_fun.reset(v)
                #generates the next serie of vignettes
                l += generate_next(s,classes,self.decision_fun,{'order':order})
        return l

    def test_generate_all(self,l):
        print('--- Testing generated sequences ---')
        def count(l,s,return_indexs=False):
            c = 0
            li = []
            for index in range(len(l)):
                for k in range(len(l[index][0])):
                    if s in l[index][0][k]:
                        c += 1
                        li.append(index)
                        break
            if return_indexs:
                return c,li
            return c
                    
        #Count names
        li = []
        for n in self.data['name']:
            li.append(count(l,n))
        print('Count names :',np.unique(li,return_counts=True))    
        assert len(np.unique(li)) == 1
        print('PASSED')
        
        #Count vignettes
        li = []
        for vtype in ['training 1','hobby 1','work 1','hobby 2']:
            for vtype2 in self.data[vtype]:
                for v in self.data[vtype][vtype2]:
                    li.append(count(l,v))
        print('Count vignettes :',np.unique(li,return_counts=True))
        assert len(np.unique(li)) == 1
        print('PASSED')
        #Count patterns
        li = []
        for i in range(len(l)):
            s = ''
            for vtype in ['training 1','hobby 1','work 1','hobby 2']:
                s += l[i][1][vtype][0]
            li.append(s)
        print('Count patterns :',np.unique(li,return_counts=True))
        assert len(np.unique(li)) == 2
        assert len(np.unique(np.unique(li,return_counts=True)[1])) == 1
        print('PASSED')
        
        #Search random vignettes
        sentences_test = []
        nb = 100
        print('Random generation :')
        for k in range(nb):
            #Generate random vignette
            li = {}
            self.decision_fun.reset()
            for vtype in ['training 1','hobby 1','work 1','hobby 2']:
                v = np.random.choice(self.data[vtype][self.decision_fun(vtype)])
                li[vtype] = v
            found = []
            for i in range(len(l)):
                flag = True
                for vtype in li:
                    if l[i][1][vtype][1] != li[vtype]:
                        flag = False
                if flag:
                    found.append(i)
            assert len(found) == 2
            assert l[found[0]][0][1:][::-1] == l[found[1]][0][1:]
            if k<2:
                print('------')
                print(l[found[0]][0][0])
                for j in range(1,len(l[found[0]][0])):
                    print('---',l[found[0]][0][j])
                print(l[found[1]][0][0])
                for j in range(1,len(l[found[1]][0])):
                    print('---',l[found[1]][0][j])
        print('PASSED')
            
        print('Random search : PASSED n=',nb)

    def generate(self):
        s = self.data["model"]
        info = {}
        classes = list(self.data.keys())
        classes.remove('model')
        for k in classes:
            if k == 'name':
                t = 'name'
                e = np.random.choice(self.data[k])
            else:
                t = self.decision_fun(k)
                e = np.random.choice(self.data[k][t])
            s = s.replace("["+k+"]",e)
            info[k] = [t,e]
        self.decision_fun.reset()
        assert s.find('[') == -1
        return s,info

    def run(self,nb):
        d = DictOfDict()
        if nb == -1:
            data = self.generate_all()
            print('generated {} lines'.format(len(data)))
            self.test_generate_all(data)
            for i in range(len(data)):
                d[str(i)]['question'] = data[i][0][0]
                d[str(i)]['answers'] = data[i][0][1:]
                d[str(i)]['info'] = data[i][1]
                d[str(i)]['keywords']['first'] = []
                d[str(i)]['keywords']['second'] = []
        else:
            for i in range(nb):
                d[str(i)]['question'],d[str(i)]['info'] = self.generate()
                d[str(i)]['answers'] = []
                d[str(i)]['keywords']['first'] = ['first']
                d[str(i)]['keywords']['second'] = [d[str(i)]['info']['hobby 2'][1],'second']
        with open(self.path_out+'.json','w') as f:
            json.dump(d,f)
        with open(self.path_out+'.txt','w') as f:
            s = ""
            for k in d:
                s += d[k]['question']+'\n'
                for a in d[k]['answers']:
                    s += a+'\n'
                s += '\n\n'
            f.write(s)

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processes the path file')
    parser.add_argument('path_in', type=str,
                        help='the path to the data file to combine')
    parser.add_argument('path_out', type=str,
                        help='the path to the data file with results of combining')
    parser.add_argument('nb',type=int,help='number of sentences to generate')
    parser.add_argument('-mode',type=str,nargs=1,default=None,help='mode of combining')
    args = parser.parse_args()

    combinator = Combinator(args.path_in,args.path_out,mode=args.mode[0])
    combinator.load()
    combinator.run(args.nb)
