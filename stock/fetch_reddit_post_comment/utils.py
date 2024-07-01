import torch
from transformers import BertTokenizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def tokenize_and_chunk(texts, tokenizer, chunk_size=512):
    encodings = []
    attention_masks = []

    for text in texts:
        tokens = tokenizer(text, truncation=False, padding=False)['input_ids']
        for i in range(0, len(tokens), chunk_size):
            chunk = tokens[i:i + chunk_size]
            encodings.append(chunk)
            attention_masks.append([1] * len(chunk))

    return encodings, attention_masks


def compute_metrics(p):
    """
    Compute metrics for model evaluation.
    """
    preds = torch.argmax(p.predictions, dim=1)
    accuracy = accuracy_score(p.label_ids, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(p.label_ids, preds, average='weighted')
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }
