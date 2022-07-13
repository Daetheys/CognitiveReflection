from curses.ascii import isdigit
import json
import re


def greene():
    """
    converts a txt file to a json one

    Format:
    -----------------------------------------
    <id of the question>. <title>

    <question main text>

    /**/ (separator)

    <id of the question>. <title>

    <question main text>

    etc.

    Example:
    -----------------------------------------
    1. Lost wallet 

    You find a lost wallet on the ground. You notice it contains information regarding the owner.
    Do you try to contact him/her?

    /**/

    2. lorem ipsum...

    """

    filepath = 'data/personal_moral'
    data = []

    with open(f'{filepath}.txt', 'r') as f:
        txt = f.read()
        txt = txt.split('/**/')
        for question in txt:
            
            # get the number just before the title
            number = int(
                "".join([c for c in question.split('.')[0] if c.isdigit()])
            )

            # get the title (just before the first .)
            title = "".join([c for c in question.split('.')[1].split('\n')[0]]).replace(
                '\t', '').replace('\n', '')
            if title.startswith(' '):
                title = title[1:]

            text = question.split(title)[1].replace('\n', '').replace('\t', '')
            
            # break the line after 12 words
            n = 12
            
            temp_text = text.split(' ')
            
            text = " ".join([[w, w+' \n'][i==n] for i, w in enumerate(temp_text)])


            data.append({'title': title, 'text': text, 'id': number})

    with open(f'{filepath}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, indent=6, ensure_ascii=False)

def cushman():
    """
    converts a txt file to a json one

    Format:
    -----------------------------------------
    <id of the question>. <title>

    <question main text>

    /**/ (separator)

    <id of the question>. <title>

    <question main text>

    etc.

    Example:
    -----------------------------------------
    1. Lost wallet 

    You find a lost wallet on the ground. You notice it contains information regarding the owner.
    Do you try to contact him/her?

    /**/

    2. lorem ipsum...

    """

    filepath = 'data/cushman_2006/items'
    data = []

    with open(f'{filepath}.txt', 'r') as f:
        txt = f.read()
        txt = txt.split('/**/')
        for question in txt:
            
            # get the number just before the title
            number = int(
                "".join([c for c in question.split('.')[0] if c.isdigit()])
            )

            # get the title (just before the first .)
            title = "".join([c for c in question.split('.')[1].split('\n')[0]]).replace(
                '\t', '').replace('\n', '')
            if title.startswith(' '):
                title = title[1:]

            text = question.split(title)[1].replace('\n', '').replace('\t', '')
            
            # change the question 
            question = text.split('.')[-1]
            question2 = question.lower().replace('is…', '')
            new = ' Is' + question2 + ' the right thing to do?'
            text = text.replace(question, new)
            text = ' '.join(text.split())

            # break the line after 12 words
            n = 12
            
            temp_text = text.split(' ')
            
            text = " ".join([[w, w+' \n'][i==n] for i, w in enumerate(temp_text)])


            data.append({'title': title, 'text': text, 'id': number})

    with open(f'{filepath}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, indent=6, ensure_ascii=False)




if __name__ == '__main__':
    cushman()
