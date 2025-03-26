import os
import queue
import sounddevice as sd
import numpy as np
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.cloud import speech
from utils import audio_generator_func, listen_and_print_responses

# Set Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "feltiv-dev-92825128d5ec.json"

# Audio Configuration
RATE = 16000  # Sampling rate
CHUNK = int(RATE / 10)  # 100ms chunks

app = FastAPI()
q = queue.Queue()

def callback(indata, frames, time, status):
    """Callback function to receive audio data"""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

@app.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    print("🎙️ Listening... Speak into the microphone.")

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with sd.RawInputStream(
        samplerate=RATE, blocksize=CHUNK, dtype="int16",
        channels=1, callback=callback
    ):
        audio_generator = (speech.StreamingRecognizeRequest(audio_content=content)
                           for content in audio_generator_func(q))
        
        responses = client.streaming_recognize(streaming_config, audio_generator)

        try:
            async for response in listen_and_print_responses(responses):
                await websocket.send_text(response)
        except WebSocketDisconnect:
            print("🛑 WebSocket disconnected. Stopping transcription.")

