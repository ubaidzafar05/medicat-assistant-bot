# ==============================================================================
# VECTOR DATABASE (Storage Engine)
# This file handles the storage and retrieval of "Memories".
# It uses Vector Embeddings: converting text into numbers so we can compare "meaning".
# Refactored to use ChromaDB for persistence and scalability.
# ==============================================================================

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import uuid

class VectorDB:
    """
    Persistent vector database using ChromaDB and sentence embeddings.
    """
    def __init__(self, embedding_model_name="sentence-transformers/all-MiniLM-L6-v2", db_path="chroma_db"):
        # Initialize the AI model that creates embeddings.
        # "all-MiniLM-L6-v2" is a small, fast model perfect for local use.
        
        # Explicitly find local cache or download if needed (simplified from previous vers)
        # We rely on sentence-transformers to handle caching logic mostly, 
        # but we can suppress some warnings or handle errors if needed.
        self.model = SentenceTransformer(embedding_model_name)
        
        self.db_path = db_path
        
        # Initialize ChromaDB Client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collection
        # We use cosine similarity to match the previous behavior (dot product of normalized vectors)
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )

    def add(self, text, source="user"):
        """
        Adds a new text to the database and updates embeddings.
        """
        # 1. Convert text to Vector (Number list)
        embedding = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0].tolist()
        
        # 2. Add to ChromaDB
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"source": source}],
            ids=[str(uuid.uuid4())]
        )

    def query(self, query_text, top_k=3):
        """
        Returns top_k most similar chunks with their sources.
        """
        if self.collection.count() == 0:
            return []

        # 1. Convert the QUESTION to a Vector
        query_vec = self.model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)[0].tolist()
        
        # 2. Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=top_k
        )
        
        # 3. Format results to match previous API
        # Chroma returns lists of lists (batch format)
        if not results["documents"]:
            return []
            
        formatted_results = []
        
        # Iterate through the first (and only) query result
        num_results = len(results["documents"][0])
        for i in range(num_results):
            score = 1 - results["distances"][0][i] # Convert cosine distance to similarity score
            formatted_results.append({
                "chunk": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "score": float(score)
            })
            
        return formatted_results

    def save(self):
        """
        No-op: ChromaDB handles persistence automatically.
        Kept for API compatibility.
        """
        pass

    def load(self):
        """
        No-op: ChromaDB handles persistence automatically.
        Kept for API compatibility.
        """
        pass

    def clear(self):
        """Wipes the database completely."""
        self.client.delete_collection("memories")
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )

