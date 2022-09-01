import streamlit as st
import numpy as np
from pandas import DataFrame
# For Flair (Keybert)
# from flair.embeddings import TransformerDocumentEmbeddings
import seaborn as sns
# For download buttons
from streamlit_func import download_button
import os
from decouple import config
from functools import partial
import openai
import sys
import argparse

from runner import Runner
# from analyser import Analyser
from model import GPTJ
from dataset import Dataset
from utils.safedict import SafeDict
from console_logger import ConsoleLogger  # ,XLSXLogger
from json_logger import JSONLogger
# from analyser import Analyser
from streamlit_func import *
from streamlit.components.v1 import html


server = config('SERVER')

# openai.api_key = config('OPENAI_API_KEY')

# -------------------------------------------------------------------------------------------------
# password
# -------------------------------------------------------------------------------------------------
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            # del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# -------------------------------------------------------------------------------------------------
# Title and header config
# -------------------------------------------------------------------------------------------------
def init():
    st.set_page_config(
        page_title="HRL LLM Playground",
        page_icon="🧠", layout="centered"
    )
    # st.sidebar.markdown("# Main 🧠")

    def _max_width_():
        max_width_str = f"max-width: 1200px; !important"
        min_width_str = f"min-width: 900px; !important"
        st.markdown(
            f"""
        <style>
        .block-container {{
            {max_width_str}
            {min_width_str}
        }}
        iframe {{
            border: none;
            outline: none;
            border-radius: 3px;
        }}
        </style>
        """, unsafe_allow_html=True
        )

    _max_width_()

# c30, c31, c32 = st.columns(3)
    c30, _, _ = st.columns([8, 1, 1])

    with c30:
        # st.image("logo.png", width=400)
        st.title("🧠  HRL GPT3 Playground")


# -------------------------------------------------------------------------------------------------
# About the app
# -------------------------------------------------------------------------------------------------
def about():
    with st.expander("Procedure", expanded=True):
        st.write(
            """
            * Upload a dataset as a .json file and formatted as follow:
                ```
                [
                    {id: [item id], title: [item title] text: [what will be prompted to the LLM]}
                ]
                ```
                Here is an [example dataset](https://raw.githubusercontent.com/Daetheys/CognitiveReflection/2b373eb9e672e09fee510d677cfc45129355974b/data/non_moral.json).
                Add as much items as you wish.

            *  Tune parameters and click run. If you want to stop the process, you should have a stop button visible in the top-right corner of this page.

            *  Enjoy talking to an AI (but beware of the Blake Lemoine syndrome).

            *  Download results!
            """
        )

        st.markdown("")

# -------------------------------------------------------------------------------------------------
# Dataset upload
# -------------------------------------------------------------------------------------------------
def upload():
    st.markdown("")
    st.markdown("## 🗎 Upload dataset  ")

    upload = st.empty()
    json_data = upload.file_uploader(label="", type=['json'])
    use_example = st.checkbox('Use example file?')
    
    if use_example:
        upload.file_uploader(label="", type=['json'], disabled=True, key=35654645)
        
        with open('data/example.json', 'rb') as f:
            data = f.read()
            class Data:
                name = 'example.json'
                data = None
                
                def __init__(self, data) -> None:
                    self.data = data
                
                def getvalue(self):
                    return self.data
            json_data = Data(data)

    st.markdown("")
    st.markdown("")
    return json_data

# -------------------------------------------------------------------------------------------------
# tweak parameters
# -------------------------------------------------------------------------------------------------
def tweak_parameters():
    # Basic configuration
    base_config = {
        # Engine
        "engine": 'text-davinci-002',  # engine being used from the API
        "temperature": 0.7,  # Temperature of the softmax sampling for the engine
        "max_tokens": 256,  # Max nb of tokens that will be processed by the engine

        # Question Configuration
        # 'full': keeps the full question // 'half': cuts the second half of the question
        "question_mode": "full",
        # [int] : nb of answers that will be shown in the prompt given to the model
        "nb_answers": 0,
        "additional_questions": ['Why?'],

        "nb_run_per_question": 1,

        # Name of the training
        "name": None,  # Name of the training
        "prefix": "",
        "data_path": None,  # Path to the training data


        "dataset_filename": json_data.name,
        "analyses": []
    }

    with st.form(key="my_form"):
        #
        ce, c1, ce, c2, c3 = st.columns([0.07, 1, 0.07, 5, 0.07])
        container = st.container()
        with c1:
            engine = st.radio(
                "Choose your model",
                ["text-davinci-002"],
                help="At present, you can choose only 1 model to embed your text. More to come!",
            )
#
            base_config['temperature'] = st.slider(
                "Temperature",
                min_value=float(.1),
                max_value=float(1),
                value=base_config['temperature'],
                help="",
            )

            base_config['question_mode'] = st.selectbox(
                label='Question mode', options=['full', 'half'])

            base_config['nb_run_per_question'] = st.slider(
                "N iteration per item",
                min_value=1,
                max_value=100,
                value=base_config['nb_run_per_question'],
                help="",
            )

            base_config['additional_questions'] = st.text_input(
                label='Additional questions (separated by question marks)',
                value=base_config['additional_questions'][0]
            )

#
        with c2:
            txt = """
            <div 
             style="width: 100%; height: 450px; background-color: #262730;
               overflow-y: scroll; white-space: pre-wrap;overflow-wrap: break-word;
               padding: 12px; color:white;  border: none; border-radius: .25rem;"
              id="output">
            </div>
            """

            st.markdown('Logs')
            st.markdown(txt, unsafe_allow_html=True)
            st.markdown('')

            progress = st.progress(0)
            submit_button = st.form_submit_button(label="✨ Run!")

            return submit_button, progress, json_data, base_config


# -------------------------------------------------------------------------------------------------
# Run the LLM
# -------------------------------------------------------------------------------------------------
def run(progress, json_data, base_config):

    param = base_config.copy()
    param['file_as_string'] = StringIO(json_data.getvalue().decode("utf-8"))
    if len(param['additional_questions'].replace(' ', '')):
        sep = '?'
        param['additional_questions'] = param['additional_questions'].strip()
        param['additional_questions'] = [
            (e+sep).strip() for e in param['additional_questions'].split(sep)]
        del param['additional_questions'][-1]
    else:
        param['additional_questions'] = []

    runner = Runner(
        param, Dataset, GPTJ,
        ConsoleLogger, JSONLogger, progress_bar=progress, logs=None)

    href = runner.save_path + '/web_logs.txt'
    script = """
        <script>
        var output = window.parent.document.getElementById('output');
        output.scrollTop = output.scrollHeight;
        setInterval(()=> {{
            function httpGet(theUrl)
            {{
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
                xmlHttp.send( null );
                return xmlHttp.responseText;
            }}
            var base_url = window.parent.location.href.replace('8501', '7000');
            var base_url = '{0}';
            var full_url = base_url + '{1}';
            var hasToScroll = output.scrollTop == output.scrollHeight - output.offsetHeight;
            output.innerHTML = httpGet(full_url);
            if (hasToScroll) {{
                output.scrollTop = output.scrollHeight;
            }}

        }}, 2500);
        </script>
        """

    script = script.format(server, href.replace('TRAININGS/', ''))

    html(script)
    # with c2:
    # st.button(label="Stop", on_click=runner.stop)

    csv, json = runner.run()
    return csv, json

# -------------------------------------------------------------------------------------------------
# Download results
# -------------------------------------------------------------------------------------------------
def download_results(csv, json):
    #
    st.markdown("## 🎈 Check & download results ")
#
    st.header("")

    cs, c1, c2,  cLast = st.columns([2, 1.5, 1.5, 2])

    with c1:
        csv_button = download_button(csv, "Data.csv", "📥 Download (.csv)")
    with c2:
        json_button = download_button(json, "Data.json", "📥 Download (.json)")


if __name__ == '__main__':
    init()

    if check_password():

        about()

        json_data = upload()

        if json_data is not None:
            submit_button, progress, json_data, base_config = tweak_parameters()

            if submit_button:
                csv, json = run(progress, json_data, base_config)

                download_results(csv, json)


# st.header("")
#
# df = (
#    DataFrame(keywords, columns=["Keyword/Keyphrase", "Relevancy"])
#    .sort_values(by="Relevancy", ascending=False)
#    .reset_index(drop=True)
# )
#
# df.index += 1
#
# Add styling
# cmGreen = sns.light_palette("green", as_cmap=True)
# cmRed = sns.light_palette("red", as_cmap=True)
# df = df.style.background_gradient(
#    cmap=cmGreen,
#    subset=[
#        "Relevancy",
#    ],
# )
#
# c1, c2, c3 = st.columns([1, 3, 1])
#
# format_dictionary = {
#    "Relevancy": "{:.1%}",
# }
#
# df = df.format(format_dictionary)
#
# with c2:
#    st.table(df)
#
#
