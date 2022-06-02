import uuid
import os
import time

from module import Module

class Runner(Module):
    def __init__(self,config,dataset,model,console_logger,json_logger,analyser):
        super().__init__(config)

        if self.config['name'] is None:
            data_file_name = self.config["data_path"].split('/')[-1].split('.')[0]
            prefix = self.config["prefix"]
            nb_trial = self.config["nb_run_per_question"]
            self.config['name'] = prefix+"-"+data_file_name+"-"+str(nb_trial)+"-"+str(uuid.uuid4())[:8]

        os.makedirs(os.path.join('TRAININGS',self.config['name']))
        
        self.dataset = dataset(self.config)
        self.model = model(self.config)
        self.console_logger = console_logger(self.config)
        self.json_logger = json_logger(self.config)

        self.analyser = analyser(self.config)

    def run(self):
        print('TRAINING STARTED : ',self.name)
        #Prepare the logger
        with self.console_logger as console_logger:
            with self.json_logger as json_logger:
                #Iter over the dataset
                for qi,q in enumerate(self.dataset):
                    json_logger.log[qi]['question'] = q.serialize()
                    #Prepare the question with the desired format
                    q.setup(self.config['question_mode'],self.config['nb_answers'])
                    #Iterate several times over each question
                    for ti in range(self.config['nb_run_per_question']):
                        #Reset the buffer of the model
                        self.model.reset_rec()
                        #Add the question to its buffer and compute the answer
                        for qaski,qask in enumerate([str(q)]+self.config['additional_questions']):
                            a,fa = self.model.ask_rec(qask)
                            json_logger.log[qi]['list'][ti]['sequence'][qaski]['prompt'] = qask
                            json_logger.log[qi]['list'][ti]['sequence'][qaski]['answer'] = fa

                        #Print results
                        console_logger.log('------>',qi,ti,':',(ti+qi*self.config['nb_run_per_question'])/(len(self.dataset)*self.config['nb_run_per_question'])*100,'%')
                        console_logger.log(self.model.rec_buffer)
        time.sleep(2)
        self.analyser.load()
        #Save the .xlsx file
        self.analyser.print_to_xlsx()
        #Save all the scores
        for score in self.config['analyses']:
            self.analyser.compute_scores(score,save=True)
        #Print the finish statement
        print('TRAINING FINISHED : ',self.name)
