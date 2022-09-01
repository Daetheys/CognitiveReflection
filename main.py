from server import CORSRequestHandler
from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import threading
# import sys
import sys
from streamlit import cli as stcli
import openai
from decouple import config


openai.api_key = config('OPENAI_API_KEY')
serv = threading.Thread(target=test, args=(CORSRequestHandler, HTTPServer,), kwargs=dict(port=7000))
serv.daemon = True
serv.start()

sys.argv = ["streamlit", "run", "main_page.py"]
sys.exit(stcli.main())



