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

from configs import *
#Define the config for the experiment
config = crt_cot.copy()
config['nb_run_per_question'] = 100
config["data_path"] = "data/new_crt_cot.json"

runner = Runner(config,Dataset,GPTJ,ConsoleLogger,JSONLogger,Analyser)

runner.run()
