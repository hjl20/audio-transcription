# audio-transcription-and-translation

Automatically prints transcribed text after selecting an audio/video file (optional: selecting a language if not in English) into the terminal.
Additionally, translates transcribed text to English if the original transcription was not in English.

- Requires input file to be in the same directory as the script file.

- Requires ffmpeg to convert file types.

Usage in terminal/cmd: transcribe.py [file]

Currently supported languages: EN, JP, KR

Libraries: speech_recognition, pydub, googletrans

