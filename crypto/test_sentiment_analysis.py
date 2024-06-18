from sentiment_analysis import analyze_sentiment

def test_analyze_sentiment():
    text = "This is a very positive test sentence."
    sentiment_score = analyze_sentiment(text)
    assert isinstance(sentiment_score, float), "Sentiment score should be a float"
    assert -1.0 <= sentiment_score <= 1.0, "Sentiment score should be between -1.0 and 1.0"

if __name__ == "__main__":
    test_analyze_sentiment()
    print("Sentiment analysis tests passed!")
