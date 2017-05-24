from collections import defaultdict
import math
import operator
from pyaudio import PyAudio
import wave

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
    'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
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
    wave_data = _record_wave_data(morse_string, bit_rate)
    print(morse_string)
    _play(wave_data, bit_rate)

def play_string_as_morse(string):
    print(string)
    morse = to_morse(string)
    play_morse(morse)

def save_morse_file(morse_string, filename='morse.wav', channels=1, sample_width=2, bit_rate=16000):
    wave_data = _record_wave_data(morse_string, bit_rate)
    wave_file = wave.open(filename, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(bit_rate)
    wave_file.writeframes(wave_data.encode())
    wave_file.close()
    return filename

def read_morse_file(filename):
    try:
        import librosa
        import numpy as np
    except ModuleNotFoundError:
        print('You need to have numpy and librosa installed to use read_morse_file')

    threshold = -8
    tone = 0
    silence = 1
    y, sr = librosa.load(filename)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=2)
    log_S = librosa.logamplitude(S, ref_power=np.max)[:1][0]

    for i, x in enumerate(log_S):
        if x > threshold:
            log_S[i] = 0
        else:
            log_S[i] = 1
    tone_flag = False
    tone_count = 0
    silence_flag = False
    silence_count = 0
    output = ''
    counts = []
    tone_dict = defaultdict(lambda: 0)
    silence_dict = defaultdict(lambda: 0)
    for tick in log_S:
        if tick == silence:
            if not silence_flag:
                silence_flag = True
                tone_flag = False
                if tone_count:
                    counts.append('t%s' % tone_count)
                    tone_dict[tone_count] += 1
                    tone_count = 0
            silence_count += 1
            output += ' '
        elif tick == tone:
            if not tone_flag:
                tone_flag = True
                silence_flag = False
                if silence_count:
                    counts.append('s%s' % silence_count)
                    silence_dict[silence_count] += 1
                    silence_count = 0
            tone_count += 1
            output += '*'
    output
    dit_range, dah_range = _tone_ranges(tone_dict)
    token_range, letter_range, word_range = _silence_ranges(silence_dict)

    morse = ''
    for item in counts:
        value = int(item[1:])
        if item.startswith('t'):
            if value in dit_range:
                morse += '.'
            elif value in dah_range:
                morse += '-'
        elif item.startswith('s'):
            if value in letter_range:
                morse += ' '
            elif value in word_range:
                morse += '   '
    print(morse)
    print(from_morse(morse))

def _tone_ranges(tone_dict):
    sorted_by_freq = sorted(
        tone_dict.items(),
        key=operator.itemgetter(1),
        reverse=True
    )
    top_two_lengths = [x[0] for x in sorted_by_freq[:2]]
    dit_length = min(top_two_lengths)

    dit_range = list(range(max(1, dit_length-1), dit_length + 2))
    dah_range = list(range(dit_length * 2, dit_length * 3 + 1))

    unused_keys = tone_dict.keys() - set(dit_range) - set(dah_range)

    for key in unused_keys:
        dit_distance = [abs(key - dit_range[0]), abs(key - dit_range[-1])]
        dah_distance = [abs(key - dah_range[0]), abs(key - dah_range[-1])]
        if min(dit_distance) <= min(dah_distance):
            dit_range.append(key)
        else:
            dah_range.append(key)

    return dit_range, dah_range

def _silence_ranges(silence_dict):
    sorted_by_freq = sorted(
        silence_dict.items(),
        key=operator.itemgetter(1),
        reverse=True
    )
    inter_token_length = min([x[0] for x in sorted_by_freq[:3]])

    inter_token_range = list(range(max(1, inter_token_length - 1), inter_token_length + 2))
    inter_letter_range = list(range(max(1, inter_token_length * 3), inter_token_length * 8 + 2))
    inter_word_range = list(range(max(1, inter_token_length * 9 - 1), inter_token_length * 24 + 2))


    unused_keys = silence_dict.keys() - set(inter_token_range) - set(inter_letter_range) - set(inter_word_range)

    for key in unused_keys:
        inter_token_distance = [abs(key - inter_token_range[0]),
                                abs(key - inter_token_range[-1])]
        inter_letter_distance = [abs(key - inter_letter_range[0]),
                                 abs(key - inter_letter_range[-1])]
        inter_word_distance = [abs(key - inter_word_range[0]),
                               abs(key - inter_word_range[-1])]

        sorted_by_min_distance = sorted(
            [(inter_token_range, min(inter_token_distance)),
             (inter_letter_range, min(inter_letter_distance)),
             (inter_word_range, min(inter_word_distance))],
            key=operator.itemgetter(1)
        )
        sorted_by_min_distance[0][0].append(key)

    return inter_token_range, inter_letter_range, inter_word_range

def _morse_list(morse_string):
    morse_string = morse_string.replace('  ', ' |')
    morse = morse_string.split(' ')
    morse = [' ' if m == '|' else m for m in morse]
    return morse

def _record_wave_data(morse_string, bit_rate):
    morse = _morse_list(morse_string)
    wave_data = ''
    end_of_letter_token = ' '
    for morse_letter in morse:
        for morse_token in morse_letter:
            wave_data += _wave_data(morse_token, bit_rate=bit_rate)
        wave_data += _wave_data(end_of_letter_token, bit_rate=bit_rate)
    return wave_data

def _wave_data(morse_token, bit_rate=16000, freq=1674.62, duration_unit=.06):
    dit = duration_unit
    dah = duration_unit * 3
    inter_gap = duration_unit
    letter_gap = duration_unit * 3
    word_gap = duration_unit * 7

    _unit_dict = {
        '.': dit,
        '-': dah,
        ' ': letter_gap,
        '  ': word_gap
    }
    unit_dict = defaultdict(lambda: dit, _unit_dict)

    morse_token_duration = unit_dict[morse_token]
    tone_tokens = ['.', '-']
    wave_data = ''

    if morse_token in tone_tokens:
        wave_data += _wave_tone_data(morse_token_duration, bit_rate, freq)
        wave_data += _wave_rest_data(inter_gap, bit_rate)
    else:
        wave_data += _wave_rest_data(morse_token_duration, bit_rate)

    return wave_data

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

