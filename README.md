pycq
=====

Morse code in python!

Requirements
--------------

requires python 3
requires portaudio and pyaudio, numpy, and librosa

on mac:
- brew install portaudio
- pip install pyaudio
- pip install numpy
- pip install librosa

Examples
---------

```
pycq $ python                                                                                                                                                                               ~/Development
Python 3.5.1 (default, Dec 26 2015, 18:08:53) 
[GCC 4.2.1 Compatible Apple LLVM 7.0.2 (clang-700.1.81)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import pycq
>>> string = 'hello world'
>>> morse = pycq.to_morse('hello to you too')
>>> morse
'.... . .-.. .-.. ---   - ---   -.-- --- ..-   - --- ---'
>>> pycq.from_morse(morse)
'HELLO TO YOU TOO'
>>> pycq.play_string_as_morse(string) # Makes some beeps
hello world
.... . .-.. .-.. ---   .-- --- .-. .-.. -..
>>> pycq.play_morse(morse) # Makes some beeps too
.... . .-.. .-.. ---   - ---   -.-- --- ..-   - --- ---
>>> pycq.save_string_as_morse_file(string, filename='from_string_morse.wav') # Creates a file of beeps
'from_string_morse.wav'
>>> pycq.save_morse_file(morse, filename='morse.wav') # Creates a file of beeps too
'morse.wav'
>>> pycq.read_morse_file('from_string_morse.wav') # Listens to file of beeps and translates
.... . .-.. .-.. ---   .-- --- .-. .-.. -..
HELLO WORLD
>>> pycq.read_morse_file('morse.wav') # Listens to file of beeps and translates
.... . .-.. .-.. ---   - ---   -.-- --- ..-   - --- ---
HELLO TO YOU TOO
>>> 
```
