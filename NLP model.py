#importing required libraries
import argparse
import io
from google.oauth2 import service_account
import pyttsx3
import speech_recognition as sr
import datetime
import moviepy.editor as mp

#starting text to speech API engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
#print(voices[0].id)
engine.setProperty('voice', voices[1].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()

#A function to greet the user according to IST time
def wishme():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning sir")
    elif hour>=12 and hour<16:
        speak("Good Afternoon sir")
    else:
        speak("Good Evening sir")
    speak("I am Rooh. How may I help you?")

#A function to convert video data to audio file named "testaudio.wav"
def video2audio():
    clip = mp.VideoFileClip("testvideo.mp4").subclip(800,900)
    clip.audio.write_audiofile("testaudio.wav")

#A function to read audio data from "testaudio.wav" to text file
def audio2text():
    r = sr.Recognizer()  #It will take audio input
    audio = 'testaudio.wav'
    with sr.AudioFile(audio) as source:
        r.pause_threshold = 0.8
        audio = r.record(source)

    try:
        query = r.recognize_google(audio, language='en-in')
        print(query)
    except Exception as e:
        print(e)
        print("Could not read properly !!\nread the file again please...")
        return("None")
    return query


#---------------Word Timestamp section----------------

credentials = service_account.Credentials.from_service_account_file('My First Project-f4f1aaacca81.json')


def transcribe_file_with_word_time_offsets(speech_file,language):
    print("Start")
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types  
    
    print("checking credentials...")
      
    client = speech.SpeechClient(credentials=credentials)
    print("Credentils Checked")

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
              
    print("audio file read")    
    
    audio = types.RecognitionAudio(content=content)
    
    print("config start")
    config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
            language_code=language,
            enable_word_time_offsets=True)
    
    print("Recognizing...")
    response = client.recognize(config, audio) 
    print("Recognized")

    for result in response.results:
        alternative = result.alternatives[0]
        print('Transcript: {}'.format(alternative.transcript))

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            print('Word: {}, start_time: {}, end_time: {}'.format(
                word,
                start_time.seconds + start_time.nanos * 1e-9,
                end_time.seconds + end_time.nanos * 1e-9))


# ----------------------Transcribing the given audio file asynchronously and output the word time offsets---------

def transcribe_gcs_with_word_time_offsets(gcs_uri,language):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code=language,
        enable_word_time_offsets=True)

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    result = operation.result(timeout=90)

    for result in result.results:
        alternative = result.alternatives[0]
        print('Transcript: {}'.format(alternative.transcript))
        print('Confidence: {}'.format(alternative.confidence))

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            print('Word: {}, start_time: {}, end_time: {}'.format(
                word,
                start_time.seconds + start_time.nanos * 1e-9,
                end_time.seconds + end_time.nanos * 1e-9))




if __name__ == '__main__':
    wishme()        #Calling wishme function to call
    video2audio()   #Calling video2audio function
    audio2text()    #Calling Audio2Text function
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(dest='audio',metavar="testaudio.wav", help='Converting audio to word time offsets')
    parser.add_argument("-s","--string", type=str, required=False)
    parser.parse_args()
    if args.path.startswith('gs://'):
        transcribe_gcs_with_word_time_offsets(args.path,args.string)
    else:
        transcribe_file_with_word_time_offsets(args.path,args.string)

#---------------DIFFERENT SECTION ENDS-------------
