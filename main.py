from http.client import responses

import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import speech_recognition as sr
from fastapi.middleware.cors import CORSMiddleware
import time
import threading
import ollama
app = FastAPI()

client = ollama.Client()
model = "llama3.2"

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

CONST_PROMPT_FOR_GRAMMAR_CORRECTION = "Check the grammar for the following sentence correct it provide any better suggestions and give response in following way: {suggestion: text, originalText: promptSentenceReceived} following is the text please do for it:"


class PromptRequest(BaseModel):
    prompt: str

@app.post("/gemini-ai/generate-registration-questions")
def generate_story(request: PromptRequest):
    try:
        response = client.generate(model, request.prompt)
        print(response.response)
        return {"generated_text": response.response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/gemini-ai/ask-suggestion")
def generate_story(request: PromptRequest):
    try:
        prompt_request = PromptRequest(prompt=CONST_PROMPT_FOR_GRAMMAR_CORRECTION + "\n" + request.prompt)
        response = client.generate(model, prompt_request)
        return {"generated_text": response.response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/gemini-ai/ask-suggestion")
def ask_suggestion(request: PromptRequest):
    try:
        prompt_with_instruction = CONST_PROMPT_FOR_GRAMMAR_CORRECTION + "\n" + request.prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_with_instruction)

        # Extracting the suggestion from the model's response
        suggestion = response.text.split("suggestion:")[1].split("originalText:")[0].strip()
        return {"suggestion": suggestion, "originalText": request.prompt}

    except Exception as e:
        return {"error": str(e)}

@app.post("/ollama/test")
def generate_story(request: PromptRequest):
    try:
       response = client.generate(model, request.prompt)
       print(response.response)
       return response.response
    except Exception as e:
        return {"error": str(e)}