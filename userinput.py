import readline
from builtins import input as dumb_input
from time import strptime


def year_type(value):
    return strptime(value, '%Y').tm_year


def input(prompt, convert_to = str, enum = None, maxretry = 3):
    prompt, convert_to = make_prompt(prompt, convert_to, enum)
    for i in range(maxretry):
        try:
            result = convert_to(dumb_input(prompt))
        except ValueError:
            continue
        if not enum or result in enum:
            return result
    raise ValueError('Aborting after ' + str(maxretry) +' tries')


def make_prompt(base, convert_to, enum):
    prompt = base
    if not enum:
        if convert_to == bool:
            convert_to = convert_to_bool
            prompt += ' (yes/no)'
    else:
        prompt += ' ' + str(enum)
    prompt += ': '
    return (prompt, convert_to)


def convert_to_bool(string):
    if string == 'yes':
        return True
    elif string == 'no':
        return False
    else:
        raise ValueError('must be "yes" or "no"')

