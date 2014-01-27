"""
Utilities for working with pitches, durations, etc.
"""

PC = [0, 2, 4, 5, 7, 9, 11]

def pitch_to_midinote(pitch):
    """Convert a humdrum pitch string such as 'AA#'
       to a MIDI note number.
    """
    note = ''.join( c for c in pitch if c not in '#-n' )

    if note.isupper():
        octave = 5 - len(note)
        scale_degree = ( ord(note[0]) - 67 ) % 7
    else:
        octave = 4 + len(note)
        scale_degree = ( ord(note[0]) - 99 ) % 7

    return 12 * octave + PC[scale_degree] + pitch.count('#') - pitch.count('-')

def recip_to_duration(recip):
    """Convert a humdrum recip string to a wholenote duration.
    """
    # Breves are indicated by zero.
    if recip[0] == '0':
        duration = 2
    else:
        duration = float(recip.rstrip('.')) ** -1

    dots = recip.count('.')

    return (2 * duration) - duration*(2.0 ** (-1 * dots))
