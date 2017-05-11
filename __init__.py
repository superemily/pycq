from collections import defaultdict
import math
from pyaudio import PyAudio

class keydefaultdict(defaultdict):
    """
    defaultdict that sets value to key for missing keys:
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
    ' ': ' ', '.': '<PERIOD>', '-': '<DASH>'
}
_FROM_MORSE = {morse: char for char, morse in _TO_MORSE.items()}

TO_MORSE = keydefaultdict(lambda x: x, _TO_MORSE)
FROM_MORSE = keydefaultdict(lambda x: x, _FROM_MORSE)

def to_morse(string):
    return ' '.join(map(lambda x: TO_MORSE[x.lower()], string))

def from_morse(morse_string):
    morse = _morse_list(morse_string)
    return ''.join(map(lambda x: FROM_MORSE[x], morse)).upper()

def play_morse(morse_string):
    bit_rate = 16000
    morse = _morse_list(morse_string)
    wave_data = ''
    end_of_letter_token = ' '
    for morse_letter in morse:
        for morse_token in morse_letter:
            wave_data += _wave_data(morse_token, bit_rate=bit_rate)
        wave_data += _wave_data(end_of_letter_token, bit_rate=bit_rate)

    print(morse_string)
    _play(wave_data, bit_rate)

def play_string_as_morse(string):
    print(string)
    morse = to_morse(string)
    play_morse(morse)

def _morse_list(morse_string):
    morse_string = morse_string.replace('  ', ' |')
    morse = morse_string.split(' ')
    morse = [' ' if m == '|' else m for m in morse]
    return morse

def _wave_tone_data(duration, bit_rate, freq):
    num_frames = int(duration * bit_rate)
    wave_data = ''
    for x in range(num_frames):
        wave_data +=  chr(
            int(math.sin(x / ((bit_rate / freq) / math.pi)) * 127 + 128)
        )
    return wave_data

def _wave_rest_data(duration, bit_rate):
    num_frames = int(duration * bit_rate)
    wave_data = ''

    for x in range(num_frames):
        wave_data += chr(128)
    return wave_data

def _wave_data(morse_token, bit_rate=16000, freq=1674.62, duration_unit=.06):
    dit = duration_unit
    dah = duration_unit * 3
    inter_gap = duration_unit
    letter_gap = duration_unit * 3
    word_gap = duration_unit * 7

    unit_dict = {
        '.': dit,
        '-': dah,
        ' ': letter_gap,
        '  ': word_gap
    }

    morse_token_duration = unit_dict[morse_token]
    tone_tokens = ['.', '-']
    wave_data = ''

    if morse_token in tone_tokens:
        wave_data += _wave_tone_data(morse_token_duration, bit_rate, freq)
        wave_data += _wave_rest_data(inter_gap, bit_rate)
    else:
        wave_data += _wave_rest_data(morse_token_duration, bit_rate)

    return wave_data

def _play(wave_data, bit_rate):
    p = PyAudio()
    stream = p.open(
        format=p.get_format_from_width(1),
        channels=1,
        rate=bit_rate,
        output=True,
    )
    for wd in wave_data:
        stream.write(wd)
    stream.stop_stream()
    stream.close()
    p.terminate()

