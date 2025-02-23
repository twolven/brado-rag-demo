from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import requests
import json
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pinecone
api_key = os.getenv("YOUR_API_KEY")
print(f"
try:
    pc = Pinecone(api_key=api_key)
    index = pc.Index(
        host="YOUR_PINECONE_ENDPOINT",
        name="YOUR_INDEX_NAME"
    )
    print("Successfully connected to Pinecone index: brado-rag-demo")
except Exception as e:
    print(f"Error connecting to Pinecone: {e}")

async def get_embeddings(text: str) -> List[float]:
    """Generate embeddings using local LM Studio instance."""
    try:
        response = requests.post(
            "http://localhost:PORT/v1/embeddings",
            headers={"Content-Type": "application/json"},
            json={
                "model": "text-embedding-nomic-embed-text-v1.5@q4_k_m",
                "input": text
            }
        )
        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            print(f"Error getting embeddings: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

async def get_relevant_context(query: str, k: int = 3) -> str:
    """Retrieve relevant context from Pinecone based on query embeddings."""
    try:
        print(f"\nProcessing query: {query}")
        
        # Generate embeddings for the query
        query_embedding = await get_embeddings(query)
        if not query_embedding:
            print("Failed to generate embeddings")
            return ""

        print("Generated embeddings successfully")

        # Search Pinecone
        print("\nSearching Pinecone...")
        results = index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )

        # Extract and combine context from results
        contexts = []
        print("\nRetrieved contexts:")
        for match in results.matches:
            print(f"\nScore: {match.score:.6f}")
            print(f"Text: {match.metadata.get('text', '')[:200]}...")  # Show first 200 chars
            # Lower the threshold to 0.6 to catch more relevant contexts
            if match.score > 0.6:
                contexts.append(match.metadata.get("text", ""))

        if not contexts:
            print("No contexts met the relevance threshold")
            return ""

        print(f"\nReturning {len(contexts)} relevant contexts")
        return "\n\n".join(contexts)

    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

async def relay_stream(response: requests.Response):
    """Relay the streaming response, ensuring complete chunks."""
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
                    json.loads(content)
                    yield content + '\n'
                except json.JSONDecodeError:
                    buffer += content
                    try:
                        json.loads(buffer)
                        yield buffer + '\n'
                        buffer = ""
                    except json.JSONDecodeError:
                        continue

def augment_messages_with_context(messages: List[Dict], context: str) -> List[Dict]:
    """Add context to the conversation messages."""
    if not context:
        return messages

    # Find the last user message
    for i in reversed(range(len(messages))):
        if messages[i]["role"] == "user":
            # Modify the user message to reference the context
            current_content = messages[i]["content"]
            messages[i]["content"] = f"Based on the context provided, {current_content}"
            
            # Insert the context as a system message
            context_message = {
                "role": "system",
                "content": f"You are a helpful AI assistant. Base your response ONLY on the following context:\n\n{context}"
            }
            messages.insert(i, context_message)
            break

    return messages

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verify LM Studio connection
        response = requests.get("http://localhost:PORT/v1/health")
        if not response.ok:
            return {"status": "error", "message": "Cannot connect to LM Studio"}, 503

        # Verify Pinecone connection
        # Use a simple query to test connection
        test_results = index.query(
            vector=[0.0] * 768,  # Zero vector
            top_k=1
        )
        
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 503

@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    try:
        body = await request.json()
        
        # Get relevant context for the last user message
        last_user_message = next(
            (msg["content"] for msg in reversed(body["messages"]) 
             if msg["role"] == "user"),
            None
        )
        
        if last_user_message:
            print("\n=== Processing New Query ===")
            print(f"User Query: {last_user_message}")
            
            context = await get_relevant_context(last_user_message)
            if context:
                print("\nAugmenting messages with context...")
                original_messages = body["messages"].copy()
                body["messages"] = augment_messages_with_context(body["messages"], context)
                
                print("\nMessage transformation:")
                print("Original messages:", json.dumps(original_messages, indent=2))
                print("\nAugmented messages:", json.dumps(body["messages"], indent=2))
            else:
                print("No relevant context found")
        
        # Forward to LM Studio
        print("\nForwarding to LM Studio...")
        response = requests.post(
            "http://localhost:PORT/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=body,
            stream=True
        )
        
        if response.status_code != 200:
            print(f"LM Studio error: {response.status_code}")
            return EventSourceResponse([
                json.dumps({"error": f"LM Studio error {response.status_code}"}) + '\n',
                '[DONE]\n'
            ])

        return EventSourceResponse(relay_stream(response))

    except Exception as e:
        print(f"Error in chat completion: {e}")
        return EventSourceResponse([
            json.dumps({"error": str(e)}) + '\n',
            '[DONE]\n'
        ])

if __name__ == "__main__":
    import uvicorn
    print("Starting RAG-enabled server on port 9215...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)