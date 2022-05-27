from curses.ascii import isdigit
import json


def main():
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
            number = int(
                "".join([c for c in question.split('.')[0] if c.isdigit()])
            )

            title = "".join([c for c in question.split('.')[1].split('\n')[0]]).replace(
                '\t', '').replace('\n', '')
            if title.startswith(' '):
                title = title[1:]

            text = question.split(title)[1].replace('\n', '').replace('\t', '')

            data.append({'title': title, 'text': text, 'id': number})

    with open(f'{filepath}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, indent=6, ensure_ascii=False)


if __name__ == '__main__':
    main()
