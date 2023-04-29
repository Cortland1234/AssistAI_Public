import pyttsx3
import speech_recognition
import datetime
import os
import requests
from requests import get
import webbrowser
import pywhatkit as kit
import pyjokes
import sys
import time
import random
from gtts import gTTS
from googletrans import Translator
from playsound import playsound
import tkinter as tk
from tkinter import *
import openai

import config #this gets the API key

openai.api_key = config.api_key
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

#function that calls for dynamic responses via openAI
def gpt_response(query):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=query,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

#This function allows the AI to speak whatever text it is given
def speak(audio):
    chatBox.insert(END, "\n\n-> AssistAI:  " + audio)
    chatBox.see("end")
    engine.say(audio)
    engine.runAndWait()

#this function handles the voice recognition and detection. converts voice to text
def command():
    recog = speech_recognition.Recognizer()

    with speech_recognition.Microphone() as source:
        chatBox.insert(END, "\n\n-> AssistAI:  Listening...")
        print('Listening...')
        recog.pause_threshold = 1
        audio = recog.listen(source, timeout=50, phrase_time_limit= 5)

    try:
        print("Voice Detected...")
        query = recog.recognize_google(audio, language= 'en-us')
        print(f"You said: {query}")

    except Exception as error:
        return "input undetected"
    return query

#this function handles the time of day and the associated greeting
def timeGreeting():
    time = int(datetime.datetime.now().hour)

    playsound("on_sound.mp3")
    if time >= 0 and time <= 12:
        speak(f"Good morning! ")
    elif time > 12 and time < 18:
        speak(f"Good afternoon! ")
    else:
        speak(f"Good evening! ")
    speak("How can I help you? Type /commands for help.")

#converts kelvin to fahrenheit
def tempConversion(kelvin):
    cel = kelvin - 273.15
    far = cel * (9/5) + 32
    return far

#gets 5 current news stories from the US
def getNews():
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=34f4da56f55c4dd2ac5ebddc13d2c33d'

    mainPage = requests.get(url).json()

    articles = mainPage["articles"]

    head = []
    day = ["first", "second", "third", "fourth", "fifth"]
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
    chatBox.insert(END, "\n\n" + "-> AssistAI:  " + translated)
    playsound("translated_text.mp3")
    os.remove("translated_text.mp3")

#Responsible for executing commands when inputted into the text box
def submitText():
    query = "-> You:  " + entry_1.get() #getting query from entry_1 box in gui

    chatBox.insert(END, "\n\n" + query)

    userInput = entry_1.get().lower()
        
    if "notepad" in userInput:
        filePath = "C:\\WINDOWS\\system32\\notepad.exe"
        os.startfile(filePath)
        speak("Opening notepad...")

    elif "/gpt " in userInput:
        question = userInput.replace("/gpt", "")
        response = gpt_response(question)
        speak(response)

    elif "command prompt" in userInput:
        speak("Opening command prompt")
        os.system("start cmd")

    elif "ip address" in userInput:
        ip = get('https://api.ipify.org').text
        speak(f"Your IP adress is {ip}")

    elif "google" in userInput:
        search = userInput.replace("google", "")
        webbrowser.open(f"{search}")
        speak("Searching" + search)

    elif "youtube" in userInput:
        searchVideo = userInput.replace("youtube", "")
        kit.playonyt(searchVideo)
        speak("Searching" + searchVideo)

    elif "date" in userInput:
        date = datetime.datetime.now()
        speak(date.strftime("Today's date is %A the %d of %B %Y"))

    elif "joke" in userInput:
        joke = pyjokes.get_joke(language="en", category="neutral")
        speak("Here's one, ")
        speak(joke)

    elif "news" in userInput:
        speak("Getting the latest news...")
        getNews()

    elif "weather" in userInput:
        if "in" in userInput:
            userInput = userInput.replace("weather in", "")
            city = userInput
            getWeather(city)
        else:
            getWeather("Las Vegas")

    elif "time" in userInput:
        now = datetime.datetime.now()
        time12 = now.strftime("%I:%M %p").lstrip("0")
        speak("The current time is " + time12)

    elif "commands" in userInput:
        chatBox.insert(END, "\n\n-> AssistAI: COMMAND LIST\n- translate (AUDIO INPUT ONLY)\n- notepad\n- /gpt\n- command prompt\n- ip address\n- google\n- youtube\n- date\n- joke\n- news\n- weather\n- time\n- commands\n- turn off\n")

    elif "turn off" in userInput:
        speak("I'm glad I could help. Have a good rest of your day. Goodbye")
        playsound("off_sound.mp3")
        sys.exit()

    else:
        speak("That is not a valid input, please try again.")

#responsible for executing various voice commands
def executeTask():

    mood = ["I am doing okay.", "I am a little tired.", "So so.", "I am doing great.", "I am happy to be here."]

    audioInput = command()
    textTranscript = "-> You:  " + audioInput #transcribes intitial audio input
    chatBox.insert(END, "\n\n" + textTranscript) #displays transcription in chatbox gui

    query = audioInput.lower()

    if "notepad" in query:
        chatBox.insert(END, "\n\n" + "-> AssistAI:  Opening notepad..")
        filePath = "C:\\WINDOWS\\system32\\notepad.exe"
        os.startfile(filePath)
        speak("Opened Notepad")

    elif "gpt" in query: #this causes AssistAI to enter GPT chat mode, which allows user to ask chatGPT anything
        speak("Starting GPT...")
        speak("What would you like to ask?")
        question = command().lower()
        gptTranscript = "-> You:  " + question
        chatBox.insert(END, "\n" + gptTranscript)
        response = gpt_response(question)
        speak(response)

    elif "command prompt" in query:
        speak("Opening command prompt")
        os.system("start cmd")

    elif "ip address" in query:
        ip = get('https://api.ipify.org').text
        speak(f"Your IP address is {ip}")

    elif "google" in query:
        speak("What should I search on google?")
        search = command().lower()
        webbrowser.open(f"{search}")
        speak("Searching " + search)

    elif "youtube" in query:
        speak("What video should I play for you?")
        search = command().lower()
        kit.playonyt(search)
        speak("Searching " + search)

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

    elif "turn off" in query:
        speak("I'm glad I could help. Have a good rest of your day. Goodbye")
        playsound("off_sound.mp3")
        sys.exit()


if __name__ == "__main__":
    # GUI window
    gui = tk.Tk()
    gui.title("AssistantAI")
    gui.geometry("500x390")

    # Main Frame
    main_Frame = tk.Frame(gui, width=400, height = 100)
    main_Frame.pack()

    scrollbar=tk.Scrollbar(gui, orient= VERTICAL)
    scrollbar.pack(side = RIGHT, fill = Y)

    # Chat output
    chatBox = tk.Text(main_Frame, width=53, height = 18, wrap=WORD, font = 'Helvetica 12', background="#FFF2F2", yscrollcommand = scrollbar.set)
    chatBox.configure(state=NORMAL)
    chatBox.insert
    chatBox.pack() 

    # User Text Input
    entry_1 = tk.Entry(main_Frame, width = 37, font = 'Helvetica 12', borderwidth=0)
    entry_1.pack(side = LEFT, padx = 10, pady = 13, ipady=5)

    # Buttons
    text_icon = PhotoImage(file = r"textSend.png")
    mic_icon = PhotoImage(file = r"micSend.png")

    button_1 = tk.Button(main_Frame, width = 50, height = 50, image=mic_icon, command=executeTask, borderwidth=0)
    button_1.pack(side=RIGHT, padx = 12, pady=10)

    button_2 = tk.Button(main_Frame, width = 50, height = 50, image = text_icon, command=submitText, borderwidth= 0)
    button_2.pack(side=RIGHT, padx = 5, pady=10)
   
    timeGreeting()
    gui.resizable(width=False, height=False)
    gui.mainloop()
