import json
import xlsxwriter
import os
import matplotlib.pyplot as plt
import numpy as np
from queue import PriorityQueue
import tensorflow as tf
import tensorflow_hub as hub

from module import Module

class Analyser(Module):
    def __init__(self,config):
        super().__init__(config)
        self.data = None
        
    def load(self):
        #Load the data
        with open(os.path.join(self.path,'data.json'),'r') as f:
            self.data = json.load(f)


        #Download and loads the model for completion_soft scoring
        module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        print('\n--- Loading model - it might take a few minutes the first time you download it and raise a few memory warnings ---\n')
        self.model = hub.load(module_url)
        

    def print_to_xlsx(self):
        #Extract a .xlsx representation of the data.json file
        self.wb = xlsxwriter.Workbook(os.path.join(self.path,'results.xlsx'))
        self.bold = self.wb.add_format({'bold':True})
        self.ws = self.wb.add_worksheet()
        self.ws.write(0,0,'Questions\Trials')
        width = 1+len(self.config['additional_questions'])
        #Iter through all questions
        for qindstr in self.data:
            #Get question prompt
            qind = int(qindstr)
            question_data = self.data[qindstr]['question']
            #Write the prompt
            if width>1:
                self.ws.merge_range(qind*width+1,0,qind*width+width,0,question_data['prompt'])
            else:
                self.ws.write(qind*width+1,0,question_data['prompt'])
            #Iter through all trials
            for trialidstr in self.data[qindstr]['list']:
                trialid = int(trialidstr)
                #Write the trial ID
                self.ws.write(0,trialid+1,trialid)
                #Iter through the sequence of sub questions
                for seqidstr in self.data[qindstr]['list'][trialidstr]['sequence']:
                    seqid = int(seqidstr)
                    results = self.data[qindstr]['list'][trialidstr]['sequence'][seqidstr]
                    #Write the prompts given to the model in bold and it answers in normal
                    self.ws.write_rich_string(qind*width+seqid+1,trialid+1,self.bold,results['prompt'],results['answer']['choices'][0]['text'])
        #Save and close the notebook
        self.wb.close()

    def compute_scores(self,mode,save=False):
        if mode == "completion_exact":
            return self.compute_scores_completion_exact(save=save)
        elif mode == "completion_soft":
            return self.compute_scores_completion_soft(save=save)

    def compute_scores_completion_exact(self,save=False):
        width = 1+len(self.config['additional_questions'])
        counts = np.array([0.]*len(self.data.keys()))
        for qindex in self.data:
            original_text = self.data[qindex]['question']['prompt']
            for trialid in self.data[qindex]['list']:
                results = self.data[qindex]['list'][trialid]['sequence']['0']
                completed_text = results['prompt']+results['answer']['choices'][0]['text']
                counts[int(qindex)] += completed_text[:len(original_text)] == original_text
        counts /= len(counts)
        #Plot the score and save it
        if save:
            fig = plt.figure()
            plt.plot(range(len(counts)),counts)
            plt.savefig(os.path.join(self.path,'completion_exact.png'))
        return counts


    def compute_scores_completion_soft(self,save=False):
        def distance(sentences):
            #Get vec representation
            vec = self.model(sentences)
            #Compute similarity matrix
            out = np.inner(vec,vec)
            #Compute Similarity score
            sim = out[0,1:].mean()
            #Compute Diversity score
            triu = np.triu_indices(out.shape[0]-1,1)
            div = out[1:,1:][triu].mean()
            #Return scores
            return sim,div

                            
        width = 1+len(self.config['additional_questions'])
        sims = np.array([0.]*len(self.data.keys()))
        divs = np.array([0.]*len(self.data.keys()))
        #Iter through all questions
        for qindex in self.data:
            #Get original question prompt
            original_text = self.data[qindex]['question']['prompt']
            #Add it to the list of sentences to be given to the model
            sentences = [original_text]
            #Iter through all trials
            for trialid in self.data[qindex]['list']:
                #Get completed text
                results = self.data[qindex]['list'][trialid]['sequence']['0']
                completed_text = results['prompt']+results['answer']['choices'][0]['text']
                completed_text = completed_text.split('\n')[0]
                #Add the completed text to the sentences to be given to the model
                sentences.append(completed_text)
            #Compute scores
            sims[int(qindex)],divs[int(qindex)] = distance(sentences)
        #Plot the scores and save them
        if save:
            fig, ax1 = plt.subplots()
            #Similarity axis
            ax1.set_xlabel('Question index')
            ax1.set_ylabel('Similarity score', color="blue")
            ax1.plot(range(len(sims)),sims,color='blue',lw=0,marker='o')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.set_ylim(0,1)
            #Diversity axis
            ax2 = ax1.twinx()
            ax2.set_ylim(0,1)
            ax2.set_ylabel('Diversity score', color="red")
            ax2.plot(range(len(divs)),divs,color='red',lw=0,marker='o')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.plot(range(len(divs)),[0.8]*len(divs),color='black',lw=1)
            fig.tight_layout()
            #Save the figure
            plt.savefig(os.path.join(self.path,'completion_partial.png'))
        return sims,divs

import argparse
if __name__ == '__main__':
    #Parse args
    parser = argparse.ArgumentParser(description='Processes the path file')
    parser.add_argument('path', type=str,
                        help='the path to the folder from a training')
    parser.add_argument('--xlsx',action='store_const',const=True,default=False,help='saves the xlsx file')
    parser.add_argument('--scores',type=str,nargs='+',default=[],help='the list of scores to be computed')
    args = parser.parse_args()
    path = args.path
    with open(os.path.join(path,'config.json'),'r') as f:
        #Load config
        config = json.load(f)
        #Load analyser
        analyser = Analyser(config)
        analyser.load()
        #Print to xlsx
        if args.xlsx:
            analyser.print_to_xlsx()
        #Compute asked scores
        for score in args.scores:
            analyser.compute_scores(score,save=True)
