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
config = cf_test3.copy()
config["data_path"] = "data/billlight.json"

runner = Runner(config,Dataset,GPTJ,ConsoleLogger,JSONLogger,Analyser)

runner.run()
