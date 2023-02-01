import pyttsx3
import speech_recognition
import datetime
import os
import requests
from requests import get
import wikipedia
import webbrowser
import pywhatkit as kit
import pyjokes
import sys
import time
import random
from gtts import gTTS
from googletrans import Translator
from playsound import playsound

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

#list contains the name of each supported language and the corresponding lang tag for the translator
langDict = (
    "af", "Afrikaans","ar", "Arabic", "bg", "Bulgarian","bn", "Bengali","bs", "Bosnian","ca", "Catalan","cs", "Czech",
    "da", "Danish","de", "German","el", "Greek","en", "English","es", "Spanish","et", "Estonian","fi", "Finnish",
    "fr", "French","gu", "Gujarati","hi", "Hindi","hr", "Croatian","hu", "Hungarian","id", "Indonesian","is", "Icelandic",
    "it", "Italian","iw", "Hebrew","ja", "Japanese","jw", "Javanese","km", "Khmer","kn", "Kannada","ko", "Korean","la", "Latin",
    "lv", "Latvian","ml", "Malayalam","mr", "Marathi","ms", "Malay","my", "Myanmar (Burmese)","ne", "Nepali","nl", "Dutch",
    "no", "Norwegian","pl", "Polish","pt", "Portuguese","ro", "Romanian","ru", "Russian","si", "Sinhala","sk", "Slovak",
    "sq", "Albanian","sr", "Serbian","su", "Sundanese","sv", "Swedish","sw", "Swahili", "ta", "Tamil","te", "Telugu",
    "th", "Thai","tl", "Filipino","tr", "Turkish","uk", "Ukrainian","ur", "Urdu","vi", "Vietnamese","zh-CN", "Chinese (Simplified)",
    "zh-TW", "Chinese (Traditional)"
)

#This function allows the AI to speak whatever text it is given
def speak(audio):
    engine.say(audio)
    print("ChatBot: " + audio)
    engine.runAndWait()


#this function handles the voice recognition and detection. converts voice to text
def command():
    recog = speech_recognition.Recognizer()

    with speech_recognition.Microphone() as source:
        print('Listening...')
        recog.pause_threshold = 1
        audio = recog.listen(source, timeout=50, phrase_time_limit= 5)

    try:
        print("Voice Detected...")
        query = recog.recognize_google(audio, language= 'en-us')
        print(f"You said: {query}")

    except Exception as error:
        print("input undetected")
        return "none"
    return query

#this function handles the time of day and the associated greeting
def timeGreeting():
    time = int(datetime.datetime.now().hour)
    now = datetime.datetime.now()
    time12 = now.strftime("%I:%M %p").lstrip("0")

    playsound("on_sound.mp3")
    if time >= 0 and time <= 12:
        speak(f"Good morning! The time is {time12}")
    elif time > 12 and time < 18:
        speak(f"Good afternoon! The time is {time12}")
    else:
        speak(f"Good evening! The time is {time12}")
    speak("I am ChatBot, your virtual assistant. Call on me for help.")

#converts kelvin to fahrenheit
def tempConversion(kelvin):
    cel = kelvin - 273.15
    far = cel * (9/5) + 32
    return far

#gets 3 current news stories
def getNews():
    url = "http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=34f4da56f55c4dd2ac5ebddc13d2c33d"

    mainPage = requests.get(url).json()

    articles = mainPage["articles"]

    head = []
    day = ["first", "second", "third"]
    for r in articles:
        head.append(r["title"])
    for i in range (len(day)):
        speak(f"Today's {day[i]} news is: {head[i]}")

#gets the weather for city
def getWeather(city):
    WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?"
    WEATHER_KEY = "81a0418b0a216a803a6374463dd3beb0"

    try:
        weatherURL = WEATHER_URL + "appid=" + WEATHER_KEY + "&q=" + city

        response = requests.get(weatherURL).json()

        #converting responses from kelvin to fahrenheit
        temp_k = response['main']['temp']
        temp_f = tempConversion(temp_k)
        round_temp = round(temp_f)
        feels_k = response['main']['feels_like']
        feels_f = tempConversion(feels_k)
        round_feels = round(feels_f)
        weatherDesc = response['weather'][0]['description']

        speak(f"Temperature in {city} is {round_temp} degrees fahrenheit and feels like {round_feels} degrees fahrenheit. The general weather in {city} is: {weatherDesc}")
    except Exception as error:
        speak("Sorry, I didn't catch that. For specific weather, please say \'weather in blank\' city")

#gets language to translate to from user
def language():
    speak("In what language?")
    lang = command()
    while (lang == "None"):
        lang = command()
    return lang

#translates user input to desired language
def translate():
    input = command().lower()
    lang = language()

    #if language not supported, it asks for another language
    while (lang not in langDict):
        speak("Sorry, that language is unsupported. Please try again")
        lang = language()

    #goes to the indexed tag for the desired language
    lang = langDict[langDict.index(lang)-1]

    translator = Translator()

    translateText = translator.translate(input, dest=lang)

    translated = translateText.text
    print(f"Translated text is: {translated}")

    speakAudio = gTTS(text=translated, lang=lang, slow=False)
    #saves audio to mp3, plays audio, then deletes the mp3
    speakAudio.save("translated_text.mp3")
    playsound("translated_text.mp3")
    os.remove("translated_text.mp3")

#responsible for executing various voice commands
def executeTask():

    response = ["I am here!", "Hello!", "Still here!", "What do you need?"]
    randResponse = random.choice(response)
    speak(randResponse)

    while True:
        helpRes = ["Anything else you need?", "Anything else?", "Do you need something else?",
                   "Is there something else you need?"]
        randRes = random.choice(helpRes)
        mood = ["I am doing okay.", "I am a little tired.", "So so.", "I am doing great.", "I am happy to be here."]
        query = command().lower()

        if "notepad" in query:
            filePath = "C:\\WINDOWS\\system32\\notepad.exe"
            os.startfile(filePath)
            speak("Opened Notepad")

        elif "open steam" in query:
            filePath = "C:\\Program Files (x86)\\Steam\\steam.exe"
            os.startfile(filePath)
            speak("Opened Steam")

        elif "command prompt" in query:
            speak("Opening command prompt")
            os.system("start cmd")

        elif "ip address" in query:
            ip = get('https://api.ipify.org').text
            speak(f"Your IP adress is {ip}")

        elif "wikipedia" in query:
            speak("Searching Wikipedia...")
            query = query.replace('wikipedia', '')
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia...")
            speak(results)

        elif "google" in query:
            speak("What should I search on google?")
            search = command().lower()
            webbrowser.open(f"{search}")
            speak("Searching" + search)

        elif "youtube" in query:
            speak("What video should I play for you?")
            search = command().lower()
            kit.playonyt(search)
            speak("Searching" + search)

        elif "date" in query:
            date = datetime.datetime.now()
            speak(date.strftime("Today's date is %A the %d of %B %Y"))

        elif "joke" in query:
            joke = pyjokes.get_joke(language="en", category="neutral")
            speak("Here's one, ")
            speak(joke)

        elif "who are you" in query:
            speak("I am an Artificial Intelligence assistant created by Cortland Deem")

        elif "how are you" in query:
            curMood = random.choice(mood)
            speak(curMood)

        elif "news" in query:
            speak("Getting the latest news...")
            getNews()

        elif "weather" in query:
            if "in" in query:
                query = query.replace("weather in", "")
                city = query
                getWeather(city)
            else:
                getWeather("Las Vegas")

        elif "time" in query:
            now = datetime.datetime.now()
            time12 = now.strftime("%I:%M %p").lstrip("0")
            speak("The current time is " + time12)

        elif "translate" in query:
            speak("Say what you want translated")
            translate()

        elif "sleep" in query:
            speak("Entering sleep mode. Call me again for help")
            break

        elif "no" in query:
            speak("Understood.")
            break

        elif "turn off" in query:
            speak("I'm glad I could help. Have a good rest of your day. Goodbye")
            playsound("off_sound.mp3")
            sys.exit()

        time.sleep(2)
        speak(randRes)

if __name__ == "__main__":
    timeGreeting()
    while True:
        query = command().lower()
        if "chatbot" in query:
            executeTask()
        elif "turn off" in query:
            speak("I'm glad I could help. Have a good rest of your day. Goodbye")
            playsound("off_sound.mp3")
            sys.exit()
