import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import asyncio
import hashlib

SIMILARITY_THRESHOLD = 1  # Adjust as needed

def generate_claim_id(claim_text):
    """Generate a unique ID for a claim based on its text."""
    return hashlib.sha256(claim_text.encode('utf-8')).hexdigest()

def insert_or_update_claim(claim_text, metadata):
    # Search for similar claims in the database
    similar_claims = langchain_chroma.similarity_search_with_score(claim_text)
    if similar_claims:
        print(similar_claims[0][1])
        if similar_claims[0][1] >= SIMILARITY_THRESHOLD:
            similar_claim = similar_claims[0][0]
            print("existing claim")
            if similar_claim.metadata!=metadata:
                similar_claim.metadata['source'] = similar_claim.metadata['source'] +" "+ metadata['source']
                langchain_chroma.update_document(similar_claim.metadata['id'], similar_claim)
    else:
        # If no similar claim, insert the new claim
        print("New claim")
        new_claim_id = generate_claim_id(claim_text)  # Implement this function
        metadata['id'] = new_claim_id
        print(new_claim_id)
        collection.add(ids=[new_claim_id], documents=[claim_text], metadatas=[metadata])

# Example usage
if __name__ == "__main__":
    # Initialize ChromaDB
    persistent_client = chromadb.Client()
    # persistent_client = chromadb.PersistentClient('./data/db')

    collection = persistent_client.get_or_create_collection("claims_collection")
    # Define an embedding function (this needs to be implemented)
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Initialize LangChain Chroma
    global langchain_chroma
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name="claims_collection",
        embedding_function=embedding_function,
    )
    # insert_or_update_claim("Earth is round", {"source": "NASA"})
    # insert_or_update_claim("earth is round in shape", {"source": "BoNASA"})
    insert_or_update_claim("earth is going to extinct", {"source": "NASA"})
    insert_or_update_claim("earth is not going to survive in comming years", {"source": "BoNASA"})
    
# store the claims
# cluster the claims
# create the knowledge graph for these claims
# implement database here

# database is not valuable here, should directly use LLM to verify whether two claims are same or not, thinking of using 