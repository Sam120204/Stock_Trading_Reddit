# gpt_sentiment.py
import openai
import config

openai.api_key = config.OPENAI_API_KEY

def analyze_sentiment(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Analyze the sentiment of the following text:\n{text}\nSentiment:",
        max_tokens=60
    )
    sentiment = response.choices[0].text.strip()
    return sentiment

# Example usage
if __name__ == "__main__":
    text = "I'm very bullish on Apple stock!"
    sentiment = analyze_sentiment(text)
    print(sentiment)
