import speech_recognition as sr
import openai
from gtts import gTTS
import pygame
import os

# Set your OpenAI API key and customize the role
openai.api_key = "your-open-ai-api-key-here"
messages = [{"role": "system", "content": "Your name is Nemo and give answers in 2 lines"}]

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Function to get response from OpenAI
def get_response(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

# Function to convert text to speech using gTTS and play with pygame
def speak_with_gtts(text):
    tts = gTTS(text=text, lang='en', slow=False)  # slow=False makes it speak faster
    tts.save("response.mp3")
    
    # Play the MP3 file using pygame
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    
    # Wait until the playback is finished
    while pygame.mixer.music.get_busy():
        continue
    
    # Remove the file after playing
    os.remove("response.mp3")

listening = True

while listening:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        recognizer.dynamic_energy_threshold = 3000

        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5.0)
            response = recognizer.recognize_google(audio)
            print(response)

            if "nemo" or "Hemo" or "memo" in response.lower():
                response_from_openai = get_response(response)
                speak_with_gtts(response_from_openai)  # Use gTTS and pygame to speak the response
            else:
                speak_with_gtts("Didn't recognize 'nemo'.")

        except sr.UnknownValueError:
            speak_with_gtts("Didn't recognize anything.")
