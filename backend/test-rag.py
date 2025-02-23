from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import requests
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def relay_stream(response: requests.Response):
    """Relay the streaming response, ensuring complete chunks"""
    buffer = ""
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                content = decoded[6:]  # Remove "data: " prefix
                if content == '[DONE]':
                    yield '[DONE]\n'
                    break
                try:
                    # Validate it's complete JSON before sending
                    json.loads(content)
                    yield content + '\n'
                except json.JSONDecodeError:
                    # If it's not complete JSON, buffer it
                    buffer += content
                    try:
                        # Try parsing the buffer
                        json.loads(buffer)
                        yield buffer + '\n'
                        buffer = ""
                    except json.JSONDecodeError:
                        continue
            else:
                print(f"Unexpected line format: {decoded}")

@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    try:
        body = await request.json()
        
        response = requests.post(
            "http://localhost:PORT/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=body,
            stream=True
        )
        
        if response.status_code != 200:
            return EventSourceResponse([
                json.dumps({"error": f"LM Studio error {response.status_code}"}) + '\n',
                '[DONE]\n'
            ])

        return EventSourceResponse(relay_stream(response))

    except Exception as e:
        return EventSourceResponse([
            json.dumps({"error": str(e)}) + '\n',
            '[DONE]\n'
        ])

if __name__ == "__main__":
    import uvicorn
    print("Starting RAG relay server on port 9215...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
