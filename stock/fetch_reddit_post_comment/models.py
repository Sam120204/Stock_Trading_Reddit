import torch
from transformers import BertForSequenceClassification
from transformers.modeling_outputs import SequenceClassifierOutput

class BertForSentimentRegression(BertForSequenceClassification):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = 1  # Sentiment score is a single continuous value
        self.classifier = torch.nn.Linear(config.hidden_size, 1)
    
    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None, labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        pooled_output = outputs[1]
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss_fct = torch.nn.MSELoss()  # Mean Squared Error loss for regression
            loss = loss_fct(logits.view(-1), labels.view(-1))
        return SequenceClassifierOutput(loss=loss, logits=logits)
