"""
Stuff for reading in Humdrum files.
Only handles basic functionality right now.
"""
import re

from midiutil.MidiFile import MIDIFile

from humpy.utils import pitch_to_midinote

pitches_re = re.compile('[ra-gA-Gn#\-]+')
durations_re = re.compile('[0-9.]+')
modifiers_re = re.compile('[^ra-gA-Gn#\-0-9.]')


class KernScore:
    """Only verified for Bach Chorales right now.
    """
    file_path = None
    reference_data = {}
    comments = []
    barlines = []

    section_order = None
    sections = []

    parts = []

    def __init__(self, file_path):
        self.file_path = file_path

        current_beat = 0

        kernfile = open(file_path)
        for line in kernfile:
            line = line.strip()

            # Parse comments.
            if line[:3] == '!!!':
                refkey = line[3:6]
                self.reference_data[refkey] = line[8:]

            elif line[:2] == '!!':
                self.comments.append(line[4:])

            elif line[0] == '!':
                # Discard inline comments.
                pass

            # Parse interpretations.
            elif '**kern' in line:
                tokens = line.split('\t')
                for token in tokens:
                    self.parts.append(new_part(token))

            elif '*IC' in line:
                for i, token in enumerate(line.split('\t')):
                    if token != '*':
                        self.parts[i]['instrumentclass'] = token

            elif '*I' in line:
                for i, token in enumerate(line.split('\t')):
                    if token != '*':
                        self.parts[i]['instrument'] = token

            elif '*k' in line:
                for i, token in enumerate(line.split('\t')):
                    self.parts[i]['keysig'] = token

            elif '*M' in line:
                for i, token in enumerate(line.split('\t')):
                    self.parts[i]['timesig'] = token

            elif '*clef' in line:
                for i, token in enumerate(line.split('\t')):
                    self.parts[i]['clef'] = token

            elif '*>[' in line:
                self.section_order = line[3:-1].split(',')

            elif '*>' in line:
                self.sections.append(new_section(line, current_beat))
                
            elif '*-' in line:
                # That's all, folks.
                pass
                
            # Parse data tokens.
            elif '=' in line:
                self.barlines.append(new_barline(line, current_beat))

            else:
                tokens = [ new_token(string, current_beat)
                           for string in line.split('\t') ]

                # Append non-null tokens to the data.
                for i, token in enumerate(tokens):
                    token and self.parts[i]['data'].append(token)

                current_beat += min( t.get('duration', float('inf'))
                                     for t in tokens )

        # Close the file.
        kernfile.close()

    def export_midi(self, file_path):
        """Export a MIDI file."""
        midi = MIDIFile(len(self.parts))

        for i, part in enumerate(self.parts):
            midi.addTrackName(i, 0, part['declaration'])
            midi.addTempo(i, 0, 100)
            
            non_rests = [ d for d in part['data'] if d['pitch'] != 'r' ]
            for note in non_rests:
                midi.addNote(track=i, channel=0,
                             pitch=note['midinote'],
                             time=note['beat'],
                             duration=note['duration'],
                             volume=100)

        with open(file_path, 'wb') as binfile:
            midi.writeFile(binfile)


# Sub-parsers / models.
def new_part(declaration):
    return { 'declaration': declaration,
             'data': [] }

def new_barline(kern_line, beat):
    """Make a new barline dict.
    """
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

def new_section(kern_line, beat):
    """Make a new section dict.
    """
    first_token = kern_line.split('\t')[0]

    return { 'beat': beat,
             'section': first_token[2:] }

def new_token(token_string, beat, timebase=4):
    """Create a new token dictionary from a kern
       token string.
    @param token_string: A single humdrum token.
    @param beat: The beat the token falls on.
    @param timebase: The recip indication of the beat note.
    @return: a token dict.
    """
    if token_string[0] == '.':
        token = {}

    else:
        pitch = ''.join(pitches_re.findall(token_string))
        duration = float(''.join(durations_re.findall(token_string)))
        modifiers = ''.join(modifiers_re.findall(token_string))

        # Breve durations are indicated with '0'.
        if duration == 0:
            duration = 0.5

        token = { 'pitch': pitch,
                  'midinote': pitch_to_midinote(pitch),
                  'duration': (float(duration) ** - 1) * timebase,
                  'recip': float(duration),
                  'modifiers': modifiers,
                  'beat': beat }

    return token
