import torch
from transformers import BertTokenizer
from models import BertForSentimentRegression  # Ensure this import is correct

# Load the fine-tuned model
model = BertForSentimentRegression.from_pretrained('finetuned_model', ignore_mismatched_sizes=True)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Use the original tokenizer

# Function to preprocess text and predict sentiment score
def predict_sentiment(text):
    model.eval()
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    inputs.pop('token_type_ids')  # Remove 'token_type_ids' if it exists
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    sentiment_score = logits.item()
    return sentiment_score

# Example usage
text = """Bearish about AAPL
Discussion
Since the launch of ChatGPT in November 2022, the number of companies citing “AI” in their earnings calls has exploded, with 199 S&P 500 companies mentioning it at least once in their Q1 2024 calls. However, management optimism still hasn’t translated to company profits.

Despite mentioning “AI” 40 times in its Q1 2024 earnings call, Adobe’s management predicted decelerating earnings and revenue growth of 12% and 10%, respectively, and its stock fell by 13.7% that day.

Similarly, Salesforce and Dell, which had both tripled between December 2022 and May 2024 on AI optimism, fell 18% and 15%, respectively, after their May earnings calls, with Morgan Stanley analysts noting that GenAI bookings still hadn’t improved Salesforce’s top line, while Bernstein analyst Toni Sacconaghi asked if Dell was selling its AI servers at zero margin, noting that its $1.7 billion in server revenue didn’t boost operating profits.

While many companies are surely to profit from AI boom such as NVIDIA from chip sales and Microsoft from cloud compute, will Apple be one of them?

Much of Apples stock boom has been around its AI hype. However, it’s still yet to see how this translates into more iPhone sales or higher profitability for the company? Are they planning to offer AI as an add-on like Samsung? There’s also the question of public’s perception of privacy concerns.

Thoughts?

Source: https://sherwood.news/business/generative-ai-consulting-war-block-trading-a24-creative-economy/

EDIT: I’m currently holding AAPL, considering selling. Here are some other concerns I have.

Import Tarifs with either Trump or Biden

Falling sales in China with market penetration from Xiaomi and Huawei

EU digital marketplace scrutiny and looming fines

Antitrust lawsuits

Diminishing marginal returns

Anyways, this is just my thesis. Would like to know more why folks are bullish to challenge this and change my mind."""


text2 = """BlackRock launches stock ETF MAXJ with 100% downside hedge . Good investment?

(Reuters) -BlackRock has launched a 'buffer' exchange-traded fund that seeks to offer a 100% downside hedge to risk-shy investors looking to tap the equity markets, the world's largest asset manager said on Monday.

So-called buffer or risk-managed ETFs help maximize returns from an asset for investors and simultaneously provide downside protection over a specific period.

The novel product will likely appeal to investors who are hoping to ride a rally in the stock markets as they continue to trade near record highs, but are concerned that a slowing economy and higher-for-longer interest rates can together hurt sentiment going forward.

Buffer ETFs also typically see lower redemption requests during times of heavy market volatility.

"BlackRock is not early - and actually is a little late - to the buffered ETF game, but with (the company's) size, reach, and marketing machine, it has a fair chance of catching up with and surpassing earlier market entrants," said Michael Ashley Schulman, partner and CIO at Running Point Capital Advisors.

"Launching buffered ETFs now, when the market is near all-time highs and many investors are nervous - especially with inflation, upcoming elections, and expanding debt - could be especially fortuitous for them," he added.

The iShares Large Cap Max Buffer Jun ETF started trading on Monday under the ticker symbol 'MAXJ'.

https://finance.yahoo.com/news/blackrock-launches-stock-etf-100-144057919.html"""

sentiment_score = predict_sentiment(text2)
print(f"Predicted Sentiment Score: {sentiment_score}")
