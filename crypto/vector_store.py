import faiss

# Function to store embeddings in FAISS
def store_embeddings(embeddings):
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    return index

# Function to retrieve similar embeddings from FAISS
def retrieve_similar(index, query_embedding, k=5):
    distances, indices = index.search(query_embedding, k)
    return distances, indices
