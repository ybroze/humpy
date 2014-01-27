"""
Utilities for working with pitches, durations, etc.
"""

PC = [0, 2, 4, 5, 7, 9, 11]

def humpitch_to_number(pitch):
    """Convert a pitch string such as 'AA' to a MIDI note number.
    """
    note = ''.join( c for c in pitch if c not in '#-n' )

    if note.isupper():
        octave = 4 - len(note)
        scale_degree = ( ord(note[0]) - 67 ) % 7
    else:
        octave = 3 + len(note)
        scale_degree = ( ord(note[0]) - 99 ) % 7

    return 12 * octave + PC[scale_degree] + pitch.count('#') - pitch.count('-')
