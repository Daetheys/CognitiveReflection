import xlrd
from json_logger import JSONLogger
import json
import argparse
import os
from question import Question

if __name__ == '__main__':

    #Parse args
    parser = argparse.ArgumentParser(description='Processes the path file')
    parser.add_argument('path', type=str,
                        help='the path to the folder from a training')
    parser.add_argument('--transpose',action='store_const',const=True,default=False,help='transpose the xlsx file')
    args = parser.parse_args()
    path = args.path
    name = path.split('/')[-2]
    
    wb = xlrd.open_workbook(os.path.join(path,'results_old.xlsx'))
    ws = wb.sheet_by_index(0)
    def get(i,j):
        return ws.cell_value(j,i)

    jsonlogger = JSONLogger({'name':name})

    with open(os.path.join(path,'config.json'),'r') as f:
        config = json.load(f)

    with jsonlogger as d:
        for i in range(ws.ncols-1):
            d.log[i]['question']['prompt'] = get(i+1,0)

        for i in range(ws.ncols-1):
            for j in range(ws.nrows-1):
                data = get(i+1,j+1)[1:]
                question = Question(d.log[i]['question']['prompt'],[])
                question.setup(prompt_mode=config['question_mode'],nb_answers=config['nb_answers'])
                str_question = str(question)
                d.log[i]['list'][j]['sequence'][0]['prompt'] = str_question
                print('-'+str_question+'-')
                print('-'+data+'-')
                d.log[i]['list'][j]['sequence'][0]['answer']['choices'] = [{'text':data[len(str_question):]}]
