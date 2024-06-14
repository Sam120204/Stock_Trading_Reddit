# import openai
# import config

# openai.api_key = config.OPENAI_API_KEY

# def analyze_sentiment(text):
#     response = openai.ChatCompletion.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": f"Analyze the sentiment of the following text:\n{text}\nSentiment:"}
#         ],
#         max_tokens=60
#     )
#     sentiment = response.choices[0].message['content'].strip()
#     return sentiment

# def analyze_correlation(data):
#     response = openai.ChatCompletion.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "You are a financial analyst."},
#             {"role": "user", "content": f"Analyze the correlation in the following dataset:\n{data}\nCorrelation analysis:"}
#         ],
#         max_tokens=150
#     )
#     correlation_analysis = response.choices[0].message['content'].strip()
#     return correlation_analysis
import openai
import config
# Initialize OpenAI with your API key
openai.api_key = config.OPENAI_API_KEY

def analyze_correlation(data):
    prompt = (
        "Here are the top 100 trending stocks and their real-time prices:\n"
        f"{data.to_dict()}\n"
        "You are a chatbot that can answer questions about these stocks based on this data. How can I help you?"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message['content']
