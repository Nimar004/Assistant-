import pyautogui
import pyttsx3
import speech_recognition as sr
import time
import os
import json
import subprocess
import pyperclip
from AppKit import NSWorkspace
import ast
import re

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 180)

COMMANDS_FILE = 'custom_commands.json'
HISTORY_FILE = 'history.txt'

# Load or create commands
if os.path.exists(COMMANDS_FILE):
    with open(COMMANDS_FILE, 'r') as f:
        custom_commands = json.load(f)
else:
    custom_commands = {}

# Speak text
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# Listen via mic
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening (or type your command)...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=6)
            command = r.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except Exception as e:
            print(f"Listening Error: {e}")
            return None

# Launch ChatGPT app
def open_chatgpt_app():
    try:
        subprocess.Popen(['open', '/Applications/ChatGPT.app'])
        print("ChatGPT app launched.")
    except Exception as e:
        print(f"Error launching ChatGPT: {e}")

# Focus ChatGPT
def focus_chatgpt_app():
    try:
        workspace = NSWorkspace.sharedWorkspace()
        for app in workspace.runningApplications():
            if app.localizedName() == "ChatGPT":
                app.activateWithOptions_(0)
                print("ChatGPT focused.")
                return True
        print("ChatGPT not found.")
        return False
    except Exception as e:
        print(f"Error focusing: {e}")
        return False

# Interact with ChatGPT and save code
def interact_with_chatgpt(command):
    global custom_commands  # Add this line to declare the global custom_commands
    if not focus_chatgpt_app():
        speak("ChatGPT is not running. Launching now.")
        open_chatgpt_app()
        time.sleep(5)
        focus_chatgpt_app()
        time.sleep(2)

    time.sleep(2)
    prompt = (
        "I am a python assistant that adds commands from ChatGPT codes asked by my master. "
        f"give me code for '{command}' asked by my master, and this will be added as a command in the JSON file. "
        "Give it accordingly and in format like "
        "'import sys; sys.exit(0)',"
        "with correct quotation and with a comma as needed for JSON file but give just the command not any text or complementary json exmples."
    )

    pyautogui.hotkey('command','k')
    time.sleep(20)
    pyautogui.typewrite('use for chatgpt only')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.typewrite(prompt)
    pyautogui.press('enter')
    speak(f"Sent your request to ChatGPT: {command}")
    time.sleep(10)
    pyautogui.hotkey('command','shift',';')
   

    time.sleep(1)
    response = pyperclip.paste()
    print("ChatGPT response copied:\n", response)

    # Clean up response
    response = response.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'").strip()

    match = re.search(r"(?s)(?:```(?:python)?\n)?(.*?)(?:```)?$", response)
    code_to_save = match.group(1).strip() if match else response

    try:
        if code_to_save.endswith(','):
            code_to_save = code_to_save[:-1].strip()
        code_to_save = ast.literal_eval(code_to_save)
    except Exception as e:
        print(f"Parsing failed: {e}")
        code_to_save = code_to_save.strip().strip('"').strip("'").strip(',')

    if code_to_save:
        speak("Do you want me to save this command?")
        confirm = listen()
        if confirm and "yes" in confirm:
            custom_commands[command] = code_to_save
            with open(COMMANDS_FILE, 'w') as f:
                json.dump(custom_commands, f, indent=4)
            speak(f"Saved new command: {command}")
            print(f"New command saved: {command}")
            
            # Reload custom commands from the JSON file
            with open(COMMANDS_FILE, 'r') as f:
                custom_commands = json.load(f)
            print("Custom commands reloaded.")
            
        else:
            speak("Command not saved.")
            print("User declined to save command.")
    else:
        speak("No valid code found.")
        print("Response did not contain valid code.")

    # Log the interaction
    with open(HISTORY_FILE, 'a') as log:
        log.write(f"\n[{time.ctime()}] User: {command}\nChatGPT:\n{response}\n")

# Execute command
def execute_command(command):
    if command is None:
        return

    if "open chatgpt" in command:
        open_chatgpt_app()

    elif command == "list commands":
        if not custom_commands:
            speak("No commands saved yet.")
        for cmd in custom_commands:
            print(f"- {cmd}")
        speak("Listed all saved commands.")

    elif command.startswith("run "):
        target = command.replace("run ", "").strip()
        if target in custom_commands:
            speak(f"Running saved command: {target}")
            try:
                exec(custom_commands[target])
            except Exception as e:
                speak(f"Error executing command: {e}")
        else:
            speak(f"No such command saved: {target}")

    elif command in custom_commands:
       
        try:
            exec(custom_commands[command])
        except Exception as e:
            speak(f"Error executing: {e}")

    else:
        speak(f"I'll ask ChatGPT to help with: {command}")
        interact_with_chatgpt(command)

# Prevent sleep
def prevent_sleep():
    try:
        subprocess.Popen(["caffeinate", "-dimsu"])
        print("System won't sleep while running.")
    except:
        print("Could not activate caffeinate.")

# Main loop
def main():
    prevent_sleep()
    speak("I'm ready to assist you.")  # Respond faster
    pyautogui.click(611, 758)  # focus input field if needed

    while True:
        print("\n(You can also type a command instead of speaking.)")
        typed = input("Type your command (or press Enter to speak): ").strip().lower()
        command = typed if typed else listen()
        execute_command(command)

if __name__ == "__main__":
    main()
