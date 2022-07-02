import sys
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

LANGUAGES = {
    'en':'en-US',
    'jp':'ja-JP',
    'kr':'ko-KR',
}

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

    #Get audio file name and type
    file_name = argv[1][:-4]
    file_type = argv[1][-3:]
    
    #Output new files into new folder
    output_folder = 'output'
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    os.path.join(output_folder)
    
    WAV_FILE = os.path.join(output_folder, convert_to_wav(file_type, file_name))
    
    r = sr.Recognizer()
    
    #Transcribe audio
    print('Transcribing.. please wait..')
    if (os.path.getsize(WAV_FILE) >> 20) > 10:
        text = get_large_wav_transcript(WAV_FILE, r, language)
    else:
        with sr.AudioFile(WAV_FILE) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language=language)
            except:
                print("Error:")
    #print(os.path.getsize(WAV_FILE) >> 20)
    
    #Print transcribed text
    print('Transcription:')
    print(text)
    #TODO: Prints translated text transcription
    if language != 'en':
        
        translated_text = ''
        print(translated_text)
    

#Convert to wav
def convert_to_wav(file_type, file_name='output'):
    WAV_FILE = file_name + '.wav'
    audio_input = AudioSegment.from_file(file_name + '.' + file_type, format=file_type)
    audio_output = os.path.join('output', WAV_FILE)
    audio_input.export(audio_output, format="wav")
    return WAV_FILE


#Split up into chunks for google's speech recognition
def get_large_wav_transcript(WAV_FILE, r, language):
    chunks, chunk_folder = split_wav_file(AudioSegment.from_wav(WAV_FILE))
    whole_text = ''
    
    #Name and save chunk files
    for i, audio_chunk in enumerate(chunks):
        chunk_name = os.path.join(chunk_folder, f'chunk{i}.wav')
        audio_chunk.export(chunk_name, format='wav')
        
        #Read chunk file
        with sr.AudioFile(chunk_name) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language)
            except sr.UnknownValueError as e:
                print("Error on {0}:".format(i))
            else:
                whole_text += text
                
        #Append chunk texts together
        whole_text += ' '

    #Clean up folder for next use
    remove_files_from(chunk_folder)
    return whole_text

   
#Split large file into chunks based on silence
def split_wav_file(WAV_FILE, min_silence_len=500, keep_silence=500):
    chunks = split_on_silence(WAV_FILE, 
                              min_silence_len=min_silence_len,
                              silence_thresh=WAV_FILE.dBFS-16,
                              keep_silence=keep_silence)
    
    #Make folder for chunks
    folder_name = 'audio-chunks'
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    return chunks, folder_name


def remove_files_from(folder):
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))
        

#Get list of audio devices
#For future use (maybe)
def list_audio_devices():
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("{0} {1}".format(index, name))
     

if __name__ == "__main__":
    main(sys.argv)