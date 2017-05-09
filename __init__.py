from collections import defaultdict

class keydefaultdict(defaultdict):
    """
    defaultdict that sets value to key for missing keys when defined:
        mydict = keydefaultdict(lambda x: x, [initial dict])
    """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            self[key] = self.default_factory(key)
            return self[key]

_TO_MORSE = {
    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.',
    'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-.', 'l': '.-..',
    'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.',
    's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
    'y': '-.--', 'z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': ' '
}
_FROM_MORSE = {morse: char for char, morse in _TO_MORSE.items()}

TO_MORSE = keydefaultdict(lambda x: x, _TO_MORSE)
FROM_MORSE = keydefaultdict(lambda x: x, _FROM_MORSE)

def to_morse(string):
    return ' '.join(map(lambda x: TO_MORSE[x], string))

def from_morse(morse_string):
    morse_string = morse_string.replace('  ', ' |')
    morse = morse_string.split(' ')
    morse = [' ' if m == '|' else m for m in morse]
    return ''.join(map(lambda x: FROM_MORSE[x], morse))

"""
What to do about capital letters? What to do about . and - as punctuation?
"""
