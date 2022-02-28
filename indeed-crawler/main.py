from json import load


FIRST_NAME = ''

if __name__ == '__main__':
    with open('default_q_and_a.json') as json:
        q_and_a = load(json)

