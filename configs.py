#Basic configuration
base_config = {
    #Engine
    "engine":'text-davinci-002', #engine being used from the API
    "temperature":0.7, #Temperature of the softmax sampling for the engine
    "max_tokens":256, #Max nb of tokens that will be processed by the engine

    #Question Configuration
    "question_mode":"full", #'full': keeps the full question // 'half': cuts the second half of the question
    "nb_answers":0, #[int] : nb of answers that will be shown in the prompt given to the model
    "additional_questions":[],

    "nb_run_per_question":2,

    #Name of the training
    "name":None, #Name of the training
    "data_path":None, #Path to the training data

    "analyses":[]
}

condition_1 = base_config.copy()
condition_1["additional_questions"] = ['Why?']

condition_4 = base_config.copy()
condition_4["question_mode"] = "half"
condition_4["analyses"] = ["completion_exact","completion_partial"]
