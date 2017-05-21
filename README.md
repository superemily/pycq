pycq
=====

Morse code in python!

Requirements
--------------

requires python 3
requires portaudio and pyaudio

on mac:
    - brew install portaudio
    - pip install pyaudio

Examples
---------

```
Python 3.6.0 (default, Dec 24 2016, 08:01:42)
[GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import pycq
>>> string = 'a kitty cat!'
>>> pycq.play_string_as_morse(string) # This will make some beeps
a kitty cat!
.-   -.- .. - - -.--   -.-. .- - !
>>> morse = pycq.to_morse(string)
>>> morse
'.-   -.- .. - - -.--   -.-. .- - !'
>>> pycq.from_morse(morse)
'A KITTY CAT!'
>>> pycq.play_morse(morse) # This will make some beeps too
.-   -.- .. - - -.--   -.-. .- - !
>>> pycq.from_morse(pycq.to_morse('Woofity woof woof!'))
'WOOFITY WOOF WOOF!'
>>>
```
