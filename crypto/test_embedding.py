from embedding import embed_text

def test_embed_text():
    text = "This is a test sentence for BERT embedding."
    embedding = embed_text(text)
    assert isinstance(embedding, (list, np.ndarray)), "Embedding should be a list or numpy array"
    assert len(embedding) > 0, "Embedding should not be empty"

if __name__ == "__main__":
    test_embed_text()
    print("Embedding tests passed!")
