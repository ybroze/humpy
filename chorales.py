"""
Stuff for finding Melodic Cadences from a Soprano Melody.
"""
import csv
from math import copysign
import re
import sys

def mean(somelist):
    return sum(somelist) / len(somelist)

class ChoraleMelody():
    """ A single chorale melody, with notes containing
        both raw and derived information.
    """
    metadata = []
    notes = []
    max_pitch = None
    min_pitch = None
    mean_dur = None

    def __init__(self, path_to_preprocessed_kern):
        self.read_melody(path_to_preprocessed_kern)

        self.get_notes_summary()
        self.add_lagged_features()

    def new_note(self, tokens):
        dur = float(tokens[3])
        semit = int(tokens[2])
        kern = str(tokens[1])
        beat = float(tokens[0])
        if ';' in kern:
            fermata = True
        else:
            fermata = False

        note = {
            'dur': dur,
            'semit': semit,
            'kern': kern,
            'beat': beat,
            'fermata': fermata,
        }

        return note

    def read_melody(self, path):
        f = open(path)

        for line in f:
            if '!!' in line:
                self.metadata.append(line)

            elif '*' not in line and '=' not in line:
                tokens = line.split('\t')
                if '.' not in tokens:
                    self.notes.append(self.new_note(tokens))

        f.close()

    def get_notes_summary(self):
        """Summary features over all notes.
        """
        self.max_pitch = max( n['semit'] for n in self.notes)
        self.min_pitch = min( n['semit'] for n in self.notes)
        self.mean_dur = mean([ n['dur'] for n in self.notes ])

    def add_lagged_features(self):
        """Time-lagged features added to each note
           in a list of notes.
        """
        for i, note in enumerate(self.notes):
            if i == 0:
                note['mint'] = None
                note['direction'] = None
                note['dur_lag1'] = None
                note['mint_lag1'] = None
                note['dur_lag2'] = None
                note['mint_lag2'] = None

            elif i == 1:
                note['mint'] = note['semit'] - self.notes[i-1]['semit']
                note['direction'] = copysign(1, note['mint'])
                note['dur_lag1'] = None
                note['mint_lag1'] = None
                note['dur_lag2'] = None
                note['mint_lag2'] = None
               
            elif i == 2:
                note['mint'] = note['semit'] - self.notes[i-1]['semit']
                note['direction'] = copysign(1, note['mint'])
                note['dur_lag1'] = self.notes[i-1]['dur']
                note['mint_lag1'] = self.notes[i-1]['mint']
                note['dur_lag2'] = None
                note['mint_lag2'] = None
              
            else:
                note['mint'] = note['semit'] - self.notes[i-1]['semit']
                note['direction'] = copysign(1, note['mint'])
                note['dur_lag1'] = self.notes[i-1]['dur']
                note['mint_lag1'] = self.notes[i-1]['mint']
                note['dur_lag2'] = self.notes[i-2]['dur']
                note['mint_lag2'] = self.notes[i-2]['mint']

    def dump_csv(self, stream):
        w = csv.writer(stream)

        keys = self.notes[0].keys()
        w.writerow(keys)

        for note in self.notes:
            w.writerow( map(note.get, keys) )           

        stream.flush()

if __name__ == '__main__':
    filepath = sys.argv[1]
    melody = ChoraleMelody(filepath)
    melody.dump_csv(sys.stdout)
