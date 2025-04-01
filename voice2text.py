import speech_recognition as sr

#convert the input audio into text
def getTextFromAudio():
    
    recognizer = sr.Recognizer()

    mic = sr.Microphone()

    try:
        with mic as source:

            recognizer.adjust_for_ambient_noise(source, duration=1)

            # Fine-tune silence detection
            recognizer.pause_threshold = 2  # Waits 2 sec after speech ends before stopping
            recognizer.non_speaking_duration = 1  # Extra 1 sec buffer before stopping

            print("Please say a command")

            audio_data = recognizer.listen(source, timeout=40)

            command = recognizer.recognize_google(audio_data)

            print(f"You said: {command}")

            return command
        
    except sr.UnknownValueError:

        print("Sorry, I couldn't understand the audio.")

        return ""
    
    except sr.RequestError:

        print("Could not request results; check your network connection.")

        return ""

#print(getTextFromAudio())