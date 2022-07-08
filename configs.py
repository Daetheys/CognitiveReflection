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
    "additional_questions":[],
    "append":"",

    "nb_run_per_question":2,

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
