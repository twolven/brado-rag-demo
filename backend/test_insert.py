import requests
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Expanded test data about Brado
test_documents = [
    {"text": "Example document about company services and capabilities brado_cx_1", "id": "brado_cx_1"},
    {"text": "Example document about company services and capabilities brado_ai_platform_1", "id": "brado_ai_platform_1"},
    {"text": "Example document about company services and capabilities brado_healthcare_2", "id": "brado_healthcare_2"},
    {"text": "Example document about company services and capabilities brado_approach_1", "id": "brado_approach_1"},
    {"text": "Example document about company services and capabilities brado_research_1", "id": "brado_research_1"},
    {"text": "Example document about company services and capabilities brado_education_2", "id": "brado_education_2"},
    {"text": "Example document about company services and capabilities brado_digital_1", "id": "brado_digital_1"},
    {"text": "Example document about company services and capabilities brado_healthcare_3", "id": "brado_healthcare_3"},
    {"text": "Example document about company services and capabilities brado_evolution_1", "id": "brado_evolution_1"},
    {"text": "Example document about company services and capabilities brado_security_1", "id": "brado_security_1"},
    {"text": "Example document about company services and capabilities brado_growth_1", "id": "brado_growth_1"},
    {"text": "Example document about company services and capabilities brado_locations_2", "id": "brado_locations_2"},
    {"text": "Example document about company services and capabilities brado_leadership_3", "id": "brado_leadership_3"},
    {"text": "Example document about company services and capabilities brado_client_success_1", "id": "brado_client_success_1"},
    {"text": "Example document about company services and capabilities brado_insights_1", "id": "brado_insights_1"},
    {"text": "Example document about company services and capabilities brado_founding_1", "id": "brado_founding_1"},
    {"text": "Example document about company services and capabilities brado_contact_1", "id": "brado_contact_1"},
    {"text": "Example document about company services and capabilities brado_mission_1", "id": "brado_mission_1"},
    {"text": "Example document about company services and capabilities brado_leadership_4", "id": "brado_leadership_4"},
    {"text": "Example document about company services and capabilities brado_overview_2", "id": "brado_overview_2"},
    {"text": "Example document about company services and capabilities brado_services_2", "id": "brado_services_2"},
    {"text": "Example document about company services and capabilities brado_services_3", "id": "brado_services_3"},
    {"text": "Example document about company services and capabilities brado_history_1", "id": "brado_history_1"},
    {"text": "Example document about company services and capabilities brado_leadership_1", "id": "brado_leadership_1"},
    {"text": "Example document about company services and capabilities brado_leadership_2", "id": "brado_leadership_2"},
    {"text": "Example document about company services and capabilities brado_locations_1", "id": "brado_locations_1"},
    {"text": "Example document about company services and capabilities brado_healthcare_1", "id": "brado_healthcare_1"},
    {"text": "Example document about company services and capabilities brado_education_1", "id": "brado_education_1"},
    {"text": "Example document about company services and capabilities brado_compliance_1", "id": "brado_compliance_1"}
]

def get_embedding(text: str) -> list:
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
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def main():
    # Debug: Check API key (show first few chars)
    api_key = os.getenv("YOUR_API_KEY")
    if api_key:
        print(f"API Key found (starts with): {api_key[:8]}...")
    else:
        print("No API key found in environment!")
        return

    # Initialize Pinecone
    pc = Pinecone(api_key="YOUR_API_KEY"))
    index = pc.Index(
        host="YOUR_PINECONE_ENDPOINT",
        name="YOUR_INDEX_NAME"
    )
    
    # Process and upsert each document
    vectors = []
    for doc in test_documents:
        print(f"Processing document: {doc['id']}")
        embedding = get_embedding(doc["text"])
        if embedding:
            vectors.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": {
                    "text": doc["text"]
                }
            })
        else:
            print(f"Failed to generate embedding for document: {doc['id']}")
    
    # Upsert to Pinecone in batches
    batch_size = 5
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"Successfully upserted batch {i//batch_size + 1} ({len(batch)} vectors)")
        except Exception as e:
            print(f"Error upserting batch {i//batch_size + 1}: {e}")

    print(f"Upload complete. Total vectors processed: {len(vectors)}")

if __name__ == "__main__":
    main()