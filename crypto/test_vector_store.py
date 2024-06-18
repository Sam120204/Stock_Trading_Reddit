import numpy as np
from vector_store import store_embeddings, retrieve_similar

def test_vector_store():
    embeddings = np.random.rand(10, 768)  # Create random embeddings for testing
    index = store_embeddings(embeddings)
    assert isinstance(index, faiss.Index), "Index should be a FAISS index"

    query_embedding = np.random.rand(1, 768)  # Create a random query embedding
    distances, indices = retrieve_similar(index, query_embedding)
    assert len(distances) > 0, "Distances should not be empty"
    assert len(indices) > 0, "Indices should not be empty"

if __name__ == "__main__":
    test_vector_store()
    print("Vector store tests passed!")
