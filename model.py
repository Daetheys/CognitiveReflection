import openai
import time
from module import Module


class Model(Module):
    def ask(self, prompt):
        raise NotImplementedError


class GPTJ(Model):
    def __init__(self, config):
        super().__init__(config)

        # Buffer that is being used to stack questions and answers to ask successive questions
        self.rec_buffer = ''

        # Errors handling
        self.error_count = 0
        self.error_count_max = 20

    def ask(self, prompt):
        try:
            # Sends a request to complete the given prompt
            answer = openai.Completion.create(engine=self.config['engine'],
                                              prompt=prompt,
                                              temperature=self.config['temperature'],
                                              max_tokens=self.config['max_tokens'], logprobs=2)
            # Extract the text from the answer
            out_text = answer.get('choices')[0].get('text')
            return out_text, answer
        except (openai.error.APIError, openai.error.ServiceUnavailableError,
         openai.error.RateLimitError) as error:  
            self.error_count += 1
            print('Error: ', error)
            if self.error_count > self.error_count_max:
                print('Too many errors')
                # assert False  # Too many errors in communicating with the server -> The process will stop to avoid spending too much money in bugs
            print('Bad GateWay -- retrying in 1sec')
            time.sleep(1)  # Wait a bit before sending another request
            return self.ask(prompt)

    def ask_rec(self, prompt):
        # Makes it possible to successively ask questions by storing them and the answers in a buffer

        # Store the new prompt in the buffer
        self.rec_buffer += "\n"+prompt
        # Ask for a completion
        out_text, answer = self.ask(self.rec_buffer)
        
        # Store the completion as well
        self.rec_buffer += out_text
        # Return the completion
        return out_text, answer

    def reset_rec(self):
        # Reset the buffer
        self.rec_buffer = ""
