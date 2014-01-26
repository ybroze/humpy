"""
Stuff for reading in Humdrum files.
Only handles basic functionality right now.
"""
import re

import pycountry

pitches_re = re.compile('[a-gA-Gr]+')
durations_re = re.compile('[0-9.]+')
modifiers_re = re.compile('[^a-zA-Zr0-9.]')

reference_data = {}
global_comments = []
comments = []
barlines = []
parts = []

def new_part(declaration):
    return { 'declaration': declaration,
             'data': [] }

def new_barline(kern_line, beat):
    barline = {'beat': beat}
    first_token = kern_line.split('\t')[0]

    if '==@' in first_token:
        barline = { 'type': 'final',
                    'number': None }
    elif '==' in first_token:
        barline = { 'type': 'double',
                    'number': first_token[2:] }
    elif '=' in first_token:
        barline = { 'type': 'single',
                    'number': first_token[1:] }

    return barline

def new_token(token_string, beat):
    """Create a new token dictionary from a kern
       token string.
    """
    if token_string == '.':
        token = {}
    else:
        pitch = ''.join(pitches_re.findall(token_string))
        duration = ''.join(durations_re.findall(token_string))
        modifiers = ''.join(modifiers_re.findall(token_string))

        token = { 'pitch': pitch,
                  'duration': float(duration),
                  'modifiers': modifiers,
                  'beat': beat }

    return token

def read_kernpath(path):
    """Only verified for Bach Chorales right now.
    """
    current_beat = 0
    with open(path) as kernfile:

        for line in kernfile:
            line = line.strip()

            # Parse comments.
            if line[:3] == '!!!':
                refkey = line[3:6]
                reference_data[refkey] = line[8:]

            elif line[:2] == '!!':
                global_comments.append(line[4:])

            elif '!' in line:
                comments[current_beat].append(line)

            # Parse interpretations.
            elif '**kern' in line:
                tokens = line.split('\t')
                for token in tokens:
                    parts.append(new_part(token))

            elif '*IC' in line:
                for i, token in enumerate(line.split('\t')):
                    if token != '*':
                        parts[i]['instrumentclass'] = token

            elif '*I' in line:
                for i, token in enumerate(line.split('\t')):
                    if token != '*':
                        parts[i]['instrument'] = token

            elif '*k' in line:
                for i, token in enumerate(line.split('\t')):
                    parts[i]['keysig'] = token

            elif '*M' in line:
                for i, token in enumerate(line.split('\t')):
                    parts[i]['timesig'] = token

            elif '*clef' in line:
                for i, token in enumerate(line.split('\t')):
                    parts[i]['clef'] = token

            elif '*-' in line:
                # That's all, folks.
                pass
                
            # Parse data tokens.
            elif '=' in line:
                barlines.append(new_barline(line, current_beat))

            else:
                tokens = [ new_token(string, current_beat)
                           for string in line.split('\t') ]

                # Append non-null tokens to the data.
                for i, token in enumerate(tokens):
                    token and parts[i]['data'].append(token)

                current_beat += max( t.get('duration', 0)
                                     for t in tokens ) ** -1
                
    # Initial import is complete. Now begin manipulating the
    # imported data into its preferred form.


