import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
from fastapi.middleware.cors import CORSMiddleware
import time
import threading

app = FastAPI()

# CORS middleware to allow requests from frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Generative AI API key
genai.configure(api_key="AIzaSyAHXD1JE6z5u3oFTHtvGCg11JyZhACFPpQ")

# Global variable to control the recording state
stop_recording = threading.Event()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/gemini-ai/generate-registration-questions")
def generate_story(request: PromptRequest):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(request.prompt)
        return {"generated_text": response.text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/speech-to-text")
def speech_to_text():
    recognizer = sr.Recognizer()
    stop_recording.clear()  # Reset the stop flag when starting recording

    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)

        print("Listening continuously for up to 120 seconds...")
        start_time = time.time()
        captured_text = ""

        try:
            while time.time() - start_time < 120 and not stop_recording.is_set():
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    text = recognizer.recognize_google(audio_data)
                    captured_text += f" {text}"
                    print(f"Recognized: {text}")
                except sr.UnknownValueError:
                    print("Could not understand the audio, continuing...")
                except sr.RequestError as e:
                    raise HTTPException(status_code=500, detail=f"Request failed: {e}")

            if stop_recording.is_set():
                print("Recording stopped by user.")

            return {"text": captured_text.strip()}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

@app.post("/stop-recording")
def stop_speech_recording():
    stop_recording.set()  # Set the stop flag
    return {"message": "Recording stopped successfully"}
