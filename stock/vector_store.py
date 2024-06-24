import faiss
import numpy as np

# Function to store embeddings in FAISS
def store_embeddings(embeddings):
    d = embeddings.shape[1]  # Assuming embeddings is a numpy array
    index = faiss.IndexFlatL2(d)  # Use IndexFlatL2 for L2 distance (Euclidean)
    index.add(embeddings)
    return index

# Function to retrieve similar embeddings from FAISS
def retrieve_similar(index, query_vector, k=15):
    D, I = index.search(query_vector.reshape(1, -1), k)
    return D, I

# Example usage
def test_vector_store():
    # Create random embeddings for testing
    embeddings = np.random.rand(10, 128).astype(np.float32)
    
    # Store embeddings in the FAISS index
    index = store_embeddings(embeddings)
    
    # Create a random query vector for testing
    query_vector = np.random.rand(128).astype(np.float32)
    
    # Retrieve similar embeddings
    D, I = retrieve_similar(index, query_vector)
    
    # Print distances and indices of the nearest neighbors
    print("Distances:", D)
    print("Indices:", I)

if __name__ == "__main__":
    test_vector_store()
