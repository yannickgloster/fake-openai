import asyncio
import json
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

streaming_response = [
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":None,"finish_reason":None}]},
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":"Hel"},"logprobs":None,"finish_reason":None}]}, 
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":"lo "},"logprobs":None,"finish_reason":None}]}, 
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":"world "},"logprobs":None,"finish_reason":None}]}, 
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":" this is a test"},"logprobs":None,"finish_reason":None}]}, 
    {"id":"fake-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{},"logprobs":None,"finish_reason":"stop"}]}
]

response = {
  "id": "fake-123",
  "object": "chat.completion",
  "created": 1741569952,
  "model": "gpt-4.1-2025-04-14",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?",
        "refusal": None,
        "annotations": []
      },
      "logprobs": None,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 10,
    "total_tokens": 29,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "service_tier": "default"
}


async def stream_generator(data: list):
    """Async generator to stream data with delays and SSE formatting."""
    for index, item in enumerate(data):
        logging.info(f"Streaming chunk #{index+1}")
        yield f"data: {json.dumps(item)}\n\n"
        if(index == 0):
            await asyncio.sleep(TIME_TILL_FIRST_CHUNK)
        elif(index != len(data) - 1):
            await asyncio.sleep(TIME_BETWEEN_CHUNKS)
    logging.info("Done streaming")

@app.get("/")
def read_root():
    return "Server is running"

TIME_TILL_FIRST_CHUNK = 1
TIME_BETWEEN_CHUNKS = 0.1

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    if "stream" in data and data["stream"]:
        logging.info(f"Streaming {len(data)} chunks")
        logging.info(f"Waiting {TIME_TILL_FIRST_CHUNK} seconds before streaming first and second chunk")
        logging.info(f"Waiting {TIME_BETWEEN_CHUNKS} seconds between subsequent chunks")
        await asyncio.sleep(TIME_TILL_FIRST_CHUNK)
        return StreamingResponse(stream_generator(streaming_response), media_type="text/event-stream")
    else:
        return Response(content=json.dumps(response), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"][
    "fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)