import json
import xlsxwriter
import os
import matplotlib.pyplot as plt
import numpy as np
from queue import PriorityQueue
import tensorflow as tf
import tensorflow_hub as hub

from module import Module
from dataset import Dataset

class Analyser(Module):
    def __init__(self,config):
        super().__init__(config)
        self.data = None
        
    def load(self):
        #Load the data
        with open(os.path.join(self.path,'data.json'),'r') as f:
            self.data = json.load(f)
        

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
        elif mode == "accuracy":
            return self.compute_accuracy_score(save=save)

    def compute_accuracy_score(self,save=False):
        width = 1+len(self.config['additional_questions'])
        keys_dict = [{} for i in range(len(self.data.keys()))]
        questions = Dataset(self.config).questions
        #Iter through all questions
        for qindex in self.data:
            #Get original question prompt
            original_text = self.data[qindex]['question']['prompt']
            #Iter through all trials
            for trialid in self.data[qindex]['list']:
                #Get completed text
                results = self.data[qindex]['list'][trialid]['sequence']['0']
                completed_text = results['answer']['choices'][0]['text']
                completed_text = completed_text.split('.')
                if len(completed_text)>1:
                    completed_text = completed_text[-2]
                else:
                    completed_text = completed_text[0]
                #Add the completed text to the sentences to be given to the model
                keywords_found = {}
                for key in questions[int(qindex)].keywords:
                    for keyword in questions[int(qindex)].keywords[key]:
                        if completed_text.find(keyword) != -1:
                            keywords_found[key] = True
                if len(keywords_found.keys()) == 1:
                    try:
                        keys_dict[int(qindex)][list(keywords_found.keys())[0]] += 1
                    except KeyError:
                        keys_dict[int(qindex)][list(keywords_found.keys())[0]] = 1
                elif len(keywords_found.keys()) > 1:
                    try:
                        keys_dict[int(qindex)]["unclear"] += 1
                    except KeyError:
                        keys_dict[int(qindex)]["unclear"] = 1
                else:
                    try:
                        keys_dict[int(qindex)]["other"] += 1
                    except KeyError:
                        keys_dict[int(qindex)]["other"] = 1

        #Plot the scores and save them
        if save:
            colors = {"intuitive":'#1f77b4',
                      "correct":'#2ca02c',
                      "other":'#ff7f0e',
                      "unclear":'#d62728'}
            #Create plot
            fig, ax1 = plt.subplots()
            #Transform keys_dict in a more readable form
            labels = {}
            for q in keys_dict:
                for k in q:
                    if not(k in ['unclear','other','correct','intuitive']):
                           labels[k] = True
            labels = list(labels.keys())
            labels.append("correct")
            labels.append("intuitive")
            labels.append("other") #Ensure unclear is present
            labels.append("unclear")
            data = np.zeros((len(self.data.keys()),len(labels)))
            for q in range(len(keys_dict)):
                for i,k in enumerate(labels):
                    try:
                        data[q][i] = keys_dict[q][k]
                    except KeyError:
                        data[q][i] = 0

            offset = np.zeros(data.shape[0])
            bars = []
            for k in range(len(labels)):
                try:
                    c = colors[labels[k]]
                except KeyError:
                    c = None
                bar = plt.bar(range(data.shape[0]),data[:,k],0.4,bottom=offset,color=c)
                bars.append(bar)
                offset += data[:,k]
            
            #Similarity axis
            ax1.set_xlabel('Question index')
            ax1.set_ylabel('Repartition')
            #Save the figure
            plt.legend(bars,labels)
            plt.title('Responses (Temperature ='+str(self.config['temperature'])+')')
            plt.savefig(os.path.join(self.path,'accuracy.png'))
        return data

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
        
        #Download and loads the model for completion_soft scoring
        module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        print('\n--- Loading model - it might take a few minutes the first time you download it and raise a few memory warnings ---\n')
        self.model = hub.load(module_url)
        
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
                completed_text = completed_text.split('?')
                if len(completed_text)>1:
                    completed_text = completed_text[0]+'?'
                else:
                    completed_text = completed_text[0]
                print("----",completed_text)
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
            ax2.set_ylabel('Consistency score', color="red")
            ax2.plot(range(len(divs)),divs,color='red',lw=0,marker='o')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.plot(range(len(divs)),[0.8]*len(divs),color='black',lw=1)
            fig.tight_layout()
            #Save the figure
            plt.title('Completion Scores (Similarity and Consistency)')
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
