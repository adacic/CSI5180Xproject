import tkinter as tk
from tkinter import scrolledtext
import voice2text as v2t
import threading
import speech_recognition as sr
import chatbot_response as c2r

mode = "title"  # Default mode

# Function to handle sending messages
def send_message():
    global mode  # Declare mode as global to access and modify the global variable
    user_message = v2t.getTextFromAudio()
    chat_window.insert(tk.END, "You: " + user_message + "\n")
    cbr = c2r.ChatbotResponse(mode)  # Create an instance of ChatbotResponse
    bot_response = "Chatbot:" + cbr.generate_response(user_message,mode) + "\n"  # Pass user_message as an argument
    chat_window.insert(tk.END, bot_response)
    chat_window.insert(tk.END, "ChatBot:Listen for the wake word...\n")  # Prompt to listen for the wake word again
    mode = cbr.c2s.mode  # Update the global mode variable

# Function to listen for the wake word
def listen_for_wake_word():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        chat_window.insert(tk.END, "ChatBot:Listen for the wake word...\n")  # Display initial message once
        while True:
            try:
                #print("Listening for wake word...")
                audio = recognizer.listen(source)
                wake_word = recognizer.recognize_google(audio).lower()
                if "wake up" in wake_word:  # Replace "wake up" with your desired wake word
                    print("Wake word detected!")
                    chat_window.insert(tk.END, "Chatbot:Wake word detected, please say a command\n")  # Display wake word detected message
                    send_message()
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                break

# Create the main window
root = tk.Tk()
root.title("Chatbot")

# Create a scrolled text widget for the chat window
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
chat_window.pack(padx=10, pady=10)

# Create an entry widget for user input
user_input = tk.StringVar()
input_entry = tk.Entry(root, textvariable=user_input, width=40)
input_entry.pack(padx=10, pady=10, side=tk.LEFT)

# Create a send button
#send_button = tk.Button(root, text="Record", command=send_message)
#send_button.pack(padx=10, pady=10, side=tk.LEFT)

# Start a separate thread to listen for the wake word
wake_word_thread = threading.Thread(target=listen_for_wake_word, daemon=True)
wake_word_thread.start()

# Run the main loop
root.mainloop()