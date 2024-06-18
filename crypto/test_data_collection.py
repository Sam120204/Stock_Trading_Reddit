from data_collection import get_reddit_data

def test_get_reddit_data():
    data = get_reddit_data(limit=10)  # Fetch a small number of posts for testing
    assert isinstance(data, list), "Data should be a list"
    assert len(data) > 0, "Data should not be empty"
    for post in data:
        assert 'title' in post, "Each post should have a title"
        assert 'body' in post, "Each post should have a body"
        assert 'score' in post, "Each post should have a score"
        assert 'created_utc' in post, "Each post should have a created_utc"
        assert 'comments' in post, "Each post should have comments"

if __name__ == "__main__":
    test_get_reddit_data()
    print("Data collection tests passed!")
