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

    filename= ['personal_moral',
                'non_moral', 'impersonal_moral']
    directory = ['data/green_2006/', ]  * len(filename)
    data = []

    for fp in [f + d for f, d in zip(directory, filename)]:
        print(fp)
        with open(f'{fp}.json', 'r') as f:
            data = json.load(f)
            for q in data:
                q['text'] += '\n (A) Yes.'
                q['text'] += '\n (B) No.'

        with open(f'{fp}_A_B.json', 'w', encoding='utf8') as f:
            json.dump(data, f, indent=6, ensure_ascii=False)


if __name__ == '__main__':
    greene()
