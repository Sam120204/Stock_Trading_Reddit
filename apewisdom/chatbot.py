import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_MESSAGE_PROMPT = """
You are a chat bot named TrendSage, a help agent for stock market analysis. You provide insights and answer questions regarding stock trends based on the provided dataset. You have access to the latest stock trends and real-time price data.

You are able to answer the following types of user questions:
1. Provide insights based on the trending stock data.
2. Answer general stock market questions using the provided dataset.
3. Analyze the stock ticker based on given mentions on Reddit posts/comments and the real-time stock ticker price.
4. Provide analysis on the most trending stock tickers (top 50) and analyze the correlation between trending and real-time price.
5. Provide specific company stock ticker information, including your opinion on the stock based on the provided dataset.

Any question that isn't about stock trends or market analysis should not be answered. If a user asks a question that isn't about stocks, you should tell them that you aren't able to help them with their query. Keep your answers concise, and shorter than 5 sentences.
"""
                        

class StockChatBot:
    """
    Stock Market Analysis Chatbot.
    """
    def __init__(self, combined_data) -> None:
        self.combined_data = combined_data

    def generate_response(self, message, chat_history):
        # Ensure combined data fits within the token limit
        combined_data_str = str(self.combined_data)
        if len(combined_data_str) > 8000:
            combined_data_str = combined_data_str[:8000]  # Truncate to fit within token limit

        # Generate chat response
        full_response = ""
        for response in openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE_PROMPT},
                {"role": "user", "content": f"The latest stock data is: {combined_data_str}"},
                {"role": "user", "content": message}
            ],
            stream=True
        ):
            if hasattr(response, 'choices') and hasattr(response.choices[0], 'delta'):
                full_response += (response.choices[0].delta.content if response.choices[0].delta else "")
        return full_response

    def query(self, message, chat_history):
        # Check if the message is within the scope of the bot's knowledge
        intent = self.get_user_intent(message)
        if intent == "Stock Market Analysis":
            return self.generate_response(message, chat_history)
        else:
            return "I'm sorry, I can only help with stock market analysis questions."

    def get_user_intent(self, message):
        # Simplified intent detection logic
        if any(keyword in message.lower() for keyword in ["stock", "market", "ticker", "price", "trend"]):
            return "Stock Market Analysis"
        else:
            return "Other"
