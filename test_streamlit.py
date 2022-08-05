import streamlit as st
from streamlit.components.v1 import html
import time

txt = """
        <textarea style="width: 100%; height: 100%; background-color: #262730; white-space: pre-wrap;overflow-wrap: break-word; color:white;  border: none;" id="output" readonly>
        </textarea>
        """
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
            //var base_url = window.parent.location.href.replace('8501', '8000');
//            var full_url = base_url + '{0}';
            //console.log(full_url);
            //output.textContent = httpGet(full_url);
            output.textContent = httpGet('http://localhost:8000/TRAININGS/non_moral.json-05_08_2022__15:45:00/log.txt');

        }}, 2000);
        </script>
        """


st.markdown(txt, unsafe_allow_html=True)
html(script)


