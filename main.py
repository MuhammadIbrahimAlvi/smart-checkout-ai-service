import threading

import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Global variable to control the recording state
stop_recording = threading.Event()

CONST_PROMPT_FOR_GRAMMAR_CORRECTION = "Check the grammar for the following sentence correct it provide any better suggestions and give response in following way: {suggestion: text, originalText: promptSentenceReceived} following is the text please do for it:"


class PromptRequest(BaseModel):
    prompt: str

@app.post("/gemini-ai/generate-registration-questions")
def generate_story(request: PromptRequest):
    try:
        response = client.generate(model, request.prompt)
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
        response = client.generate(model, prompt_with_instruction)

        # Extracting the suggestion from the model's response
        suggestion = response.response.split("suggestion:")[1].split("originalText:")[0].strip()
        return {"suggestion": suggestion, "originalText": request.prompt}

    except Exception as e:
        return {"error": str(e)}

@app.post("/conversational-talk")
def generate_story(request: PromptRequest):
    try:
       response = client.generate(model, request.prompt)
       return response.response
    except Exception as e:
        return {"error": str(e)}