import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import pyjokes
import webbrowser
import datetime

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to make Jarvis speak
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to listen to user commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("Listening timed out, no speech detected.")
            return None
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your internet connection.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

# Function to execute commands
def execute_command(command):
    if command is None:
        return  # No command detected, skip

    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")

    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today's date is {current_date}")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("Please say what you want to search.")

    elif "play" in command:
        song = command.replace("play", "").strip()
        if song:
            speak(f"Playing {song} on YouTube")
            pywhatkit.playonyt(song)
        else:
            speak("Please specify a song name.")

    elif "who is" in command or "what is" in command:
        query = command.replace("who is", "").replace("what is", "").strip()
        try:
            info = wikipedia.summary(query, sentences=2)
            speak(info)
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find any information on that.")

    elif "tell me a joke" in command:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        exit()

    else:
        speak("I'm sorry, I didn't understand that. Please try again.")

# Main function to run the assistant
def main():
    speak("I'm ready to assist you.")
    while True:
        command = listen()
        if command:
            execute_command(command)

if __name__ == "__main__":
    main()
