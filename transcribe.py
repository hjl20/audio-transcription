import sys
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from googletrans import Translator, constants


LANGUAGES = {
    'en':'en-US',
    'jp':'ja-JP',
    'kr':'ko-KR',
}

r = sr.Recognizer()

def main(argv):
    
    #Arg validation
    if len(argv) < 2:
        print('Please specify video file')
        return
    #print(sys.argv)
    
    #Set the language of the audio
    language = LANGUAGES['en']
    if len(argv) > 2:
        if argv[2] in LANGUAGES.keys():
            language = LANGUAGES[argv[2]]
        else:
            print('''
                  Invalid language key
                  Currently supporting:
                  ''')
            print(LANGUAGES.keys())
            return
    
    #Output wav files into new folder
    wav_folder = create_folder('wav-output')
    os.path.join(wav_folder)
    
    WAV_FILE = convert_to_wav(argv[1], wav_folder)
    WAV_FILE_PATH = os.path.join(wav_folder, WAV_FILE)
    
    #Transcribe audio
    print('Transcribing.. please wait..')
    if (os.path.getsize(WAV_FILE_PATH) >> 20) > 10:
        text = get_large_wav_transcript(WAV_FILE_PATH, language)
    else:
        with sr.AudioFile(WAV_FILE_PATH) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language=language)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
    
    #Print transcribed text
    print('Transcription:')
    print(text)
    
    #Prints translated text transcription
    if language != LANGUAGES['en']:
        
        tl = Translator()
        detection = tl.detect(text)
        src_lang = detection.lang
        translated_text = tl.translate(text, src=src_lang).text
        
        print(f'Translation from {constants.LANGUAGES[src_lang].capitalize()} ({detection.confidence * 100}% confidence):')
        print(translated_text)



def create_folder(name):
    output_folder = name
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    return output_folder
    

#Convert to wav
def convert_to_wav(file, wav_folder):
    file_name = file[:-3]
    file_type = file[-3:]
    
    WAV_FILE_PATH = file_name + 'wav'
    audio_input = AudioSegment.from_file(
        file_name + file_type,
        format=file_type)
    audio_output = os.path.join(wav_folder, WAV_FILE_PATH)
    audio_input.export(audio_output, format="wav")
    return WAV_FILE_PATH


#Split up into chunks for Google's speech recognition
def get_large_wav_transcript(WAV_FILE_PATH, language):
    chunks, chunk_folder = split_wav_file(WAV_FILE_PATH)
    whole_text = ''
    
    #Name and save chunk files
    for i, audio_chunk in enumerate(chunks):
        chunk_name = os.path.join(chunk_folder, f'chunk{i}.wav')
        audio_chunk.export(chunk_name, format='wav')
        
        #Read chunk file
        with sr.AudioFile(chunk_name) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language=language)
            except sr.UnknownValueError as e:
                print(f'Error on {i}:', str(e))
            else:
                print(chunk_name, ":", text)
                whole_text += text
                
        #Append text chunks together
        whole_text += ' '

    #Clear folder for next use
    remove_files_from(chunk_folder)
    return whole_text

   
#Split large file into chunks based on silence
def split_wav_file(WAV_FILE_PATH, min_silence_len=500, keep_silence=500):
    audio = AudioSegment.from_wav(WAV_FILE_PATH)
    chunks = split_on_silence(audio, 
                              min_silence_len=min_silence_len,
                              silence_thresh=audio.dBFS-16,
                              keep_silence=keep_silence)
    
    #Make folder for chunks
    chunks_folder = create_folder('audio-chunks')
    return chunks, chunks_folder


def remove_files_from(folder):
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))

     

if __name__ == '__main__':
    main(sys.argv)