import os
from decouple import config
from functools import partial
import openai
openai.api_key = config('OPENAI_API_KEY')

from dataset import Dataset
from model import GPTJ
from console_logger import ConsoleLogger#,XLSXLogger
from json_logger import JSONLogger
from runner import Runner
from analyser import Analyser

from configs import base_config,condition_1,condition_4

#Define the config for the experiment
config = condition_1.copy()
config["data_path"] = "data/data2.txt"
config["nb_run_per_question"] = 100
config["temperature"] = 1

runner = Runner(config,Dataset,GPTJ,ConsoleLogger,JSONLogger,Analyser)

runner.run()
