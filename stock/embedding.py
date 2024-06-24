import re
from transformers import BertTokenizer, BertModel
import torch

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Text cleaning function
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    return text.lower()

# Function to tokenize and embed text using BERT
def embed_text(text):
    cleaned_text = clean_text(text)
    inputs = tokenizer(cleaned_text, return_tensors='pt', padding=True, truncation=True)
    outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
