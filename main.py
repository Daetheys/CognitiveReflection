from decouple import config
from functools import partial
import openai
import sys
from PyQt5 import QtWidgets
import argparse

from runner import Runner
from gui import RunnerWindow, Communicate
from model import GPTJ
from dataset import Dataset
from utils.safedict import SafeDict
from console_logger import ConsoleLogger  # ,XLSXLogger
from json_logger import JSONLogger
from analyser import Analyser

openai.api_key = config('OPENAI_API_KEY')


# Basic configuration
base_config = SafeDict(**{
    # Engine
    "engine": 'text-davinci-002',  # engine being used from the API
    "temperature": 0.7,  # Temperature of the softmax sampling for the engine
    "max_tokens": 256,  # Max nb of tokens that will be processed by the engine

    # Question Configuration
    # 'full': keeps the full question // 'half': cuts the second half of the question
    "question_mode": "full",
    # [int] : nb of answers that will be shown in the prompt given to the model
    "nb_answers": 0,
    "additional_questions": [],

    "nb_run_per_question": 20,

    # Name of the training
    "name": None,  # Name of the training
    "prefix": "",
    "data_path": None,  # Path to the training data

    "analyses": []
})


def main(args):

    # TODO: select config file/dataset and save path from ui
    exp_name = 'items'

    param = base_config.copy()
    param["additional_questions"] = ['Why?']
    param["prefix"] = exp_name
    param["data_path"] = f"data/cushman_2006/{exp_name}.json"

    if args.gui:
        # bridge between ui and runner
        communicate = Communicate() 

        runner = Runner(param, Dataset, GPTJ,
            ConsoleLogger, JSONLogger, Analyser, communicate=communicate)

        app = QtWidgets.QApplication(sys.argv)
        win = RunnerWindow(runner=runner, communicate=communicate)
        win.setGeometry(100, 200, 800, 1000)
        sys.exit(app.exec_())

    # is executed when args.gui is False
    runner = Runner(
        param, Dataset, GPTJ,
        ConsoleLogger, JSONLogger, Analyser, communicate=None)

    runner.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', '-ui', action='store_true')
    args = parser.parse_args()
    main(args)
