# gpt_sentiment.py
import openai
import config

openai.api_key = config.OPENAI_API_KEY

def analyze_sentiment(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the sentiment of the following text:\n{text}\nSentiment:"}
        ],
        max_tokens=60
    )
    sentiment = response.choices[0].message['content'].strip()
    return sentiment

# Example usage
if __name__ == "__main__":
    text = "I'm very bullish on Apple stock!"
    sentiment = analyze_sentiment(text)
    print(sentiment)
