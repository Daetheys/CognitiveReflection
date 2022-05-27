import sys
import uuid
import os
import threading

from module import Module


class Runner(Module, threading.Thread):
    def __init__(self, config, dataset, model, logger, ui=None):
        super().__init__(config)
        threading.Thread.__init__(self)

        if self.config['name'] is None:
            self.config['name'] = str(uuid.uuid4())

        os.makedirs(os.path.join('TRAININGS', self.config['name']))

        self.dataset = dataset(self.config)
        self.model = model(self.config)
        self.logger = logger(self.config)
        
        self.ui = ui 

    def run(self):
        print('TRAINING STARTED : ', self.name)
        # Prepare the logger
        with self.logger as logger:
            # Iter over the dataset
            for qi, q in enumerate(self.dataset):
                # Prepare the question with the desired format
                q.setup(self.config['question_mode'],
                        self.config['nb_answers'])
                # Iterate several times over each question
                for i in range(self.config['nb_run_per_question']):
                    # Reset the buffer of the model
                    self.model.reset_rec()
                    # Add the question to its buffer and compute the answer
                    a1 = self.model.ask_rec(str(q))

                    if self.config['question_mode'] == 'full':
                        # Ask why in the buffer and compute the answer
                        a2 = self.model.ask_rec('\nWhy ?')
                        # Log results
                        logger.log(self.model.rec_buffer, x=i+0, y=qi+1)
                    else:
                        # Log results with bold characters
                        logger.log(logger.bold, self.model.rec_buffer[:len(
                            str(q))+1], self.model.rec_buffer[len(str(q))+1:], x=i+0, y=qi+1)
                    logger.log('---------'*4)
                    
                    print('------>', qi, i, ':', (i+qi*self.config['nb_run_per_question'])/(
                        len(self.dataset)*self.config['nb_run_per_question'])*100, '%')
                    print(self.model.rec_buffer)
                    
                    if self.ui is not None:
                        self.ui.update_prog.emit(qi/len(self.dataset)*100)
                        self.ui.update_logs.emit(self.model.rec_buffer)

        if self.ui is not None:
            self.ui.update_prog(100)
        print('TRAINING FINISHED : ', self.name)


    def stop(self):
        self._stopped = True

    def stopped(self):
        return self._stopped

