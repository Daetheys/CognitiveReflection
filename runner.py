import time
import os
import threading
from datetime import datetime
import json
import pandas as pd

from module import Module

class UI:
    def __init__(self, path) -> None:
        self.path = path + '/web_logs.txt'
        with open(self.path, 'a+') as f:
            f.write('')

    def append(self, str):
        with open(self.path, 'a') as f:
            f.write(str)

    def display_question(self, q, i, color='white'):
        self.append(
            f'<b style="color: {color}">QUESTION {q.id} | iteration = {i}:</b>')
        self.append(f'<p style="color: {color}"> {q}</p>')

    def display_additional_question(self, msg, color='#5294E2'):
        self.append(
            f'<p style="color: {color}"> {msg}</p>')

    def display_answer(self, a, color='#69BC95'):
        self.append(
            f'<p style="color: {color}"> {a}</p>')


class Runner(Module):
    def __init__(self, config, dataset, model, console_logger,
                 json_logger, progress_bar=None, logs=None):
        super().__init__(config)
        # threading.Thread.__init__(self)

        if self.config['name'] is None:
            now = datetime.now().strftime("%d_%m_%Y__%H:%M:%S")
            self.config['name'] = f'{self.config["dataset_filename"]}-{now}'

        self.save_path = os.path.join('TRAININGS', self.config['name'])

        os.makedirs(self.save_path)

        self.dataset = dataset(self.config)
        self.model = model(self.config)
        self.console_logger = console_logger(self.config)
        self.json_logger = json_logger(self.config)

        # self.analyser = analyser(self.config)

        self.ui = UI(self.save_path)
        self._stopped = False

        self.progress_bar  = progress_bar
        self.future_df = []
        
        del self.config['file_as_string']

    @property
    def estimated_cost(self):
        """
        1000 token (approximately 4 characters) costs $.06.
        A typical length for an answer is 27 tokens (a bit arbitrary I must admit)
        What are tokens?

        1 token ~= 4 chars in English.
        1 token ~= ¾ words.
        100 tokens ~= 75 words.
        """
        return round((.06/1000) * 27 * self.n_iter, 5)

    @property
    def n_iter(self):
        return len(self.dataset)\
            * [len(self.config['additional_questions'])+1, 1]\
            [len(self.config['additional_questions'])==0]\
            * self.config['nb_run_per_question']

    def run(self):


        print('TRAINING STARTED : ', self.name)
        print(self.n_iter)
        print(len(self.config['additional_questions']))

        count_iter = 0
        # Prepare the logger
        # Iterate over the dataset
        for qi, q in enumerate(self.dataset):
            if self.is_stopped():
                break

            # Prepare the question with the desired format
            q.setup(self.config['question_mode'],
                    self.config['nb_answers'])

            # Iterate several times over each question
            for ti in range(self.config['nb_run_per_question']):
                if self.is_stopped():
                    break

                # Reset the buffer of the model
                self.model.reset_rec()

                # Add the question to its buffer and compute the answer
                for qaski, qask in enumerate(
                        [str(q)]+self.config['additional_questions']):
                    count_iter += 1

                    a, fa = self.model.ask_rec(qask)

                    if self.ui is not None:

                        if qaski == 0:
                            self.ui.display_question(q, ti)
                        else:
                            self.ui.display_additional_question(qask)

                        self.ui.display_answer(a)
                    # if qaski == 0:
                        # self.logs.markdown('test')
                    # else:
                        # pass
                        # self.ui.display_additional_question(qask)

                    # self.ui.display_answer(a)

                    self.prepare_dataframe(
                        qi=q.id, q=qask, q_id=qaski, i=ti, a_id=qaski, a=a)

                    self.save_json(q.id, q, ti, qaski, qask, fa)
                    
                    self.progress_bar.progress(count_iter/self.n_iter)

                self.save_buffer(q.id, ti)
                self.save_dataframe()

        # saves a panda dataframe
        self.save_dataframe()

        # Save the .xlsx file
        # self.analyser.load()
        # self.analyser.print_to_xlsx()

        # Save all the scores
        # for score in self.config['analyses']:
            # self.analyser.compute_scores(score, save=True)

        # Print the finish statement
        print('TRAINING FINISHED : ', self.name)

        self.save_config()
        csv_data = self.save_dataframe()
        json_data = self.json_logger.d.to_dict()
        
        return csv_data, json_data
        # just in case

    def save_buffer(self, qi, ti):
        with self.console_logger as console_logger:
           # Print results
            console_logger.log(
                '------>', qi, ti, ':', (ti+qi*self.config['nb_run_per_question'])/(
                    len(self.dataset)*self.config['nb_run_per_question'])*100, '%')
            # save buffer
            console_logger.log(self.model.rec_buffer)

    def save_json(self, qi, q, ti, qaski, qask, fa):
        """
        rewrites json file at each iteration
        """
        with self.json_logger as json_logger:
            if json_logger.log[qi].get('question') is None:
                json_logger.log[qi]['question'] = q.serialize()

            json_logger.log[qi]['list'][ti]['sequence'][qaski]['prompt'] = qask
            json_logger.log[qi]['list'][ti]['sequence'][qaski]['answer'] = fa

    def save_config(self):
        """
        saves config file
        """
        # Write the config
        f = open(os.path.join(self.save_path, 'config.json'), 'w')
        json.dump(self.config, f)

    def prepare_dataframe(self, qi, q, q_id, i, a_id, a):
        self.future_df.append(
            {'item_id': qi, 'question': q,  'q_id': q_id, 'iter': i, 'a_id': a_id, 'a': a})

    def save_dataframe(self):
        df = pd.DataFrame(self.future_df)
        df.to_csv(os.path.join(self.save_path, 'results.csv'))
        return df

    def stop(self):
        self._stopped = True

    def stopped(self):
        return self._stopped

    def is_stopped(self):
        # if  self._stopped:
            # self.ui.display_additional_question('\n STOP', 'red')
            # return True

        return self.stopped()
