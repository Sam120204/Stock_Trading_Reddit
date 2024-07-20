import pandas as pd
from transformers import BertTokenizer
from datasets import Dataset
import utils  # Ensure utils.py is correctly set up

# Load the dataset
df = pd.read_csv('reddit_data_with_sentiment.csv')

# Filter out rows without valid sentiment scores
valid_sentiments = df['sentiment'].apply(lambda x: x.replace('.', '', 1).replace('-', '', 1).isdigit())  # Check if the sentiment can be converted to float
df = df[valid_sentiments]

# Preprocess data to include context and scores
def create_composite_text(row):
    composite_text = (
        f"Title: {row['post_title']} (Score: {row['post_score']})\n"
        f"Body: {row['post_body']}\n"
        "Below is all comments:\n"
    )
    
    if pd.notna(row['comment_body']):
        composite_text += f"Comment: {row['comment_body']} (Score: {row['comment_score']})\n"
        if pd.notna(row['reply_body']):
            composite_text += f"Reply: {row['reply_body']} (Score: {row['reply_score']})\n"
                
    return composite_text

df['composite_text'] = df.apply(create_composite_text, axis=1)
df['labels'] = df['sentiment'].astype(float)  # Ensure sentiment scores are floats

# Tokenize and chunk the data
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
max_length = 512

def tokenize_and_chunk(text):
    tokens = tokenizer(text, truncation=False, padding=False, max_length=None)
    input_ids = tokens['input_ids']
    attention_masks = tokens['attention_mask']
    
    chunks = []
    for i in range(0, len(input_ids), max_length):
        chunk_input_ids = input_ids[i:i + max_length]
        chunk_attention_mask = attention_masks[i:i + max_length]
        
        # Padding for the last chunk if it's smaller than max_length
        if len(chunk_input_ids) < max_length:
            padding_length = max_length - len(chunk_input_ids)
            chunk_input_ids += [tokenizer.pad_token_id] * padding_length
            chunk_attention_mask += [0] * padding_length
        
        chunks.append((chunk_input_ids, chunk_attention_mask))
    return chunks

# Apply tokenization and chunking
all_input_ids = []
all_attention_masks = []
all_labels = []

for _, row in df.iterrows():
    text = row['composite_text']
    chunks = tokenize_and_chunk(text)
    label = row['labels']
    
    for chunk_input_ids, chunk_attention_mask in chunks:
        all_input_ids.append(chunk_input_ids)
        all_attention_masks.append(chunk_attention_mask)
        all_labels.append(label)

# Ensure the lengths match
assert len(all_input_ids) == len(all_attention_masks) == len(all_labels)

# Split into train and test datasets
split_idx = int(0.8 * len(all_input_ids))
train_input_ids = all_input_ids[:split_idx]
train_attention_masks = all_attention_masks[:split_idx]
train_labels = all_labels[:split_idx]
test_input_ids = all_input_ids[split_idx:]
test_attention_masks = all_attention_masks[split_idx:]
test_labels = all_labels[split_idx:]

# Save datasets
train_dataset = Dataset.from_dict({
    'input_ids': train_input_ids, 
    'attention_mask': train_attention_masks,
    'labels': train_labels
})
test_dataset = Dataset.from_dict({
    'input_ids': test_input_ids, 
    'attention_mask': test_attention_masks,
    'labels': test_labels
})

train_dataset.save_to_disk('train_dataset')
test_dataset.save_to_disk('test_dataset')
