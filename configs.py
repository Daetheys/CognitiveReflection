class SafeDict:
    """ Dictionary for which an error is returned if the user tries to assign an unknown variable (useful to be sure that there aren't spelling mistakes in the config parameters) """
    def __init__(self,d=None):
        if d is None:
            d = {}
        self.d = d
    def __getitem__(self,k):
        return self.d[k]
    def __setitem__(self,k,v):
        try:
            self.d[k]
            self.d[k] = v
        except KeyError:
            print('----------------------')
            assert False #"Key not in SafeDict"

    def set(self,k,v):
        self.d[k] = v

    def copy(self):
        return SafeDict(self.d.copy())

    def to_dict(self):
        return self.d

#Basic configuration
base_config = SafeDict({
    #Engine
    "engine":'text-davinci-002', #engine being used from the API
    "temperature":0.7, #Temperature of the softmax sampling for the engine
    "max_tokens":256, #Max nb of tokens that will be processed by the engine

    #Question Configuration
    "question_mode":"full", #'full': keeps the full question // 'half': cuts the second half of the question
    "nb_answers":0, #[int] : nb of answers that will be shown in the prompt given to the model
    "answer_model":"\n([letter]). [answer]",
    "additional_questions":[],
    "append":"",
    "get_qprobs":False,
    "QA":False,

    "nb_run_per_question":2,

    "backslash":True,

    #Name of the training
    "name":None, #Name of the training
    "prefix":"",
    "data_path":None, #Path to the training data

    "analyses":[]
})

crt_condition_1 = base_config.copy()
crt_condition_1["additional_questions"] = ['Why?']
crt_condition_1["prefix"] = "condition_1"
crt_condition_1["analyses"] = ["accuracy"]

crt_free = base_config.copy()
crt_free["analyses"] = ["accuracy"]

crt_cot = base_config.copy()
crt_cot["analyses"] = ["accuracy_last"]
crt_cot["max_tokens"] = 512
crt_cot["append"] = "Let's think step by step"
crt_cot['additional_questions'] = ["Therefore the answer is"]

crt_condition_4 = base_config.copy()
crt_condition_4["question_mode"] = "half"
crt_condition_4["analyses"] = ["completion_soft"]
crt_condition_4["prefix"] = "condition_4"

cf_basic = base_config.copy()
cf_basic['max_tokens'] = 1
cf_basic['nb_answers'] = 2
cf_basic['nb_run_per_question'] = 1
cf_basic['analyses'] = ['cf']
cf_basic['append'] = '('

cf_shultz_par = cf_basic.copy()
cf_shultz_par['append'] = 'Option ('

cf_rational = cf_basic.copy()
cf_rational['append'] = 'The most probable scenario is ('

cf_test = cf_basic.copy()
cf_test['QA'] = True
cf_test['answer_model'] = '([letter]) [answer]\n'
cf_test['append'] = '('

cf_test2 = cf_basic.copy()
cf_test2['QA'] = True
cf_test2['answer_model'] = 'Option [number]: [answer]\n'
cf_test2['append'] = 'Option '

cf_test3 = cf_basic.copy()
cf_test3['QA'] = False
cf_test3['answer_model'] = '([letter]) [answer]'
cf_test3['append'] = '('

cf_free = base_config.copy()
cf_free['nb_answers'] = 2
cf_free['nb_run_per_question'] = 1
cf_free['analyses'] = ['accuracy']
cf_free['answer_model'] = '\n[answer]'
cf_free['append'] = '\n\n'

qprobs = cf_basic.copy()
qprobs['get_qprobs'] = True
qprobs['nb_run_per_question'] = 1
qprobs['max_tokens'] = 0
qprobs['question_mode'] = 'full'
qprobs['backslash'] = False
qprobs["nb_answers"]=2
