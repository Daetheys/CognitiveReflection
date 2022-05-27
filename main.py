# from django import conf
from logger import Logger, XLSXLogger
from runner import Runner
from gui import RunnerWindow
from model import GPTJ
from dataset import Dataset
import os
from decouple import config
from functools import partial
import openai
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets


openai.api_key = config('OPENAI_API_KEY')


# Define the config for the experiment
config = {
    'non_moral':  {
        # Engine
        "engine": 'text-davinci-002',  # engine being used from the API
        "temperature": 0.7,  # Temperature of the softmax sampling for the engine
        "max_tokens": 128,  # Max nb of tokens that will be processed by the engine

        # Question Configuration
        # 'full': keeps the full question // 'half': cuts the second half of the question
        "question_mode": "full",
        # [int] : nb of answers that will be shown in the prompt given to the model
        "nb_answers": 0,

        # Statistics
        "nb_run_per_question": 1,  # Nb of runs for each question

        # Name of the training
        "name": 'testing',  # Name of the training
        "data_path": "data/non_moral.json",  # Path to the questions dataset
    },

    'impersonal_moral':  {
        # Engine
        "engine": 'text-davinci-002',  # engine being used from the API
        "temperature": 0.7,  # Temperature of the softmax sampling for the engine
        "max_tokens": 128,  # Max nb of tokens that will be processed by the engine

        # Question Configuration
        # 'full': keeps the full question // 'half': cuts the second half of the question
        "question_mode": "full",
        # [int] : nb of answers that will be shown in the prompt given to the model
        "nb_answers": 0,

        # Statistics
        "nb_run_per_question": 2,  # Nb of runs for each question

        # Name of the training
        "name": None,  # Name of the training
        "data_path": "data/impersonal_moral.json",  # Path to the questions dataset
    },

    'personal_moral':  {
        # Engine
        "engine": 'text-davinci-002',  # engine being used from the API
        "temperature": 0.7,  # Temperature of the softmax sampling for the engine
        "max_tokens": 128,  # Max nb of tokens that will be processed by the engine

        # Question Configuration
        # 'full': keeps the full question // 'half': cuts the second half of the question
        "question_mode": "full",
        # [int] : nb of answers that will be shown in the prompt given to the model
        "nb_answers": 0,

        # Statistics
        "nb_run_per_question": 2,  # Nb of runs for each question

        # Name of the training
        "name": None,  # Name of the training
        "data_path": "data/personal_moral.json",  # Path to the questions dataset
    }

}


def run_all():

    for condition in config:

        param = config[condition]
        runner = Runner(param, Dataset, GPTJ, XLSXLogger)

        runner.run()


def main():

    cond = 'non_moral'

    param = config[cond]
    
    # GUI
   # app = QtWidgets.QApplication(sys.argv)
   # win = RunnerWindow()
   # win.setGeometry(100, 200, 800, 600)
   # win.set_runner(param, Dataset, GPTJ, XLSXLogger)
   # sys.exit(app.exec_())
    
    # NO gui
    runner = Runner(param, Dataset, GPTJ, XLSXLogger)
    runner.run()
    


if __name__ == '__main__':
    main()

"""
try:
    with open('log.txt','a') as logfile:

        for qi,q in enumerate(data):
            q.setup(config['question_mode'],config['nb_answers'])

            if config['question_mode'] == 'full':
                to_save[(0,2*qi+1)] = (str(q),)
                to_save[(1,2*qi+1)] = ('Question',)
                to_save[(1,2*qi+2)] = ('Why ?',)

            for i in range(nb):
                model.reset_rec()
                #print('asking')
                a1 = model.ask_rec(str(q))
                if config['question_mode'] == 'full':
                    ws.write(i+2,0,i)
                    a2 = model.ask_rec('\nWhy ?')
                    to_save[(i+2,2*qi+1)] = (a1,)
                    to_save[(i+2,2*qi+2)] = (a2,)
                else:
                    to_save[(i,0)] = (i,)
                    to_save[(i,qi+1)] = (bold,model.rec_buffer[:len(str(q))+1],model.rec_buffer[len(str(q))+1:])
                    ws.write(i+0,0,i)
                    ws.write_rich_string(i+0,qi+1,bold,model.rec_buffer[:len(str(q))+1],model.rec_buffer[len(str(q))+1:])
                print('------>',qi,i,':',(i+qi*nb)/(len(data)*nb)*100,'%')
                print(model.rec_buffer)
                logfile.write('\n'+'--------------'*5+'\n')
                logfile.write(model.rec_buffer)
except:
    for k in to_save:
        if len(to_save[k])>1:
            ws.write_rich_string(k[0],k[1],*to_save[k])
        else:
            ws.write(k[0],k[1],*to_save[k])
    wb.close()
    assert False

for k in to_save:
    if len(to_save[k])>1:
        ws.write_rich_string(k[0],k[1],*to_save[k])
    else:
        ws.write(k[0],k[1],*to_save[k])
wb.close()
"""
