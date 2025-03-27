import queue
from google.cloud import speech

def audio_generator_func(q: queue.Queue):
    """Generate audio chunks for processing"""
    while True:
        data = q.get()
        if data is None:
            return
        yield data

async def listen_and_print_responses(responses):
    """Listen for responses and send them over WebSocket"""
    for response in responses:
        if not response.results:
            continue

        for result in response.results:
            if result.is_final:
                transcript = f"✅ Final: {result.alternatives[0].transcript}"
                yield transcript
            else:
                transcript = f"📝 Interim: {result.alternatives[0].transcript}"
                yield transcript
