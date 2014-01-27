"""
Stuff for reading in Humdrum files.
Only handles basic functionality right now.
"""
import re

from midiutil.MidiFile import MIDIFile

from humpy.utils import pitch_to_midinote, recip_to_duration

pitches_re = re.compile('[ra-gA-Gn#\-]+')
recip_re = re.compile('[0-9.]+')
modifiers_re = re.compile('[^ra-gA-Gn#\-0-9.]')


class KernScore:
    """Only verified for Bach Chorales right now.
    """
    file_path = None
    metadata = {}
    comments = []
    barlines = []

    section_order = None
    sections = []

    parts = []

    def __init__(self, file_path):
        self.file_path = file_path

        # Partwise markers.
        next_beats = []

        kernfile = open(file_path)
        for line in kernfile:
            line = line.strip()

            # Parse comments.
            if line[:3] == '!!!':
                refkey = line[3:6]
                self.metadata[refkey] = line[8:]

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
                    next_beats.append(0)

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
                self.sections.append(new_section(line, min(next_beats)))
                
            elif '*-' in line:
                # That's all, folks.
                pass
                
            # Parse data tokens.
            elif '=' in line:
                self.barlines.append(new_barline(line, min(next_beats)))

            else:
                tokens = [ new_token(string, next_beats[i])
                           for i, string in enumerate(line.split('\t')) ]

                # Append non-null tokens to the data.
                for i, token in enumerate(tokens):

                    token and self.parts[i]['data'].append(token)
                    next_beats[i] += token.get('duration', 0)


        # Close the file.
        kernfile.close()

    def export_midi(self, file_path):
        """Export a MIDI file."""
        midi = MIDIFile(1)
        midi.addTrackName(0, 0, self.metadata.get('OTL'))
        midi.addTempo(0, 0, 80)

        for i, part in enumerate(self.parts):
            non_rests = [ d for d in part['data'] if d['pitch'] != 'r' ]
            for note in non_rests:
                midi.addNote(track=1, channel=i,
                             pitch=note['midinote'],
                             time=note['beat'],
                             duration=note['duration'],
                             volume=80)

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
        modifiers = ''.join(modifiers_re.findall(token_string))
        recip = ''.join(recip_re.findall(token_string))

        token = {
            'pitch': pitch,
            'recip': recip,
            'midinote': pitch_to_midinote(pitch),
            'duration': recip_to_duration(recip) * timebase,
            'beat': beat,
            'modifiers': modifiers,
        }

    return token
