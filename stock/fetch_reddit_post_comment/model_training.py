import torch
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_from_disk
from transformers.modeling_outputs import SequenceClassifierOutput

# Load datasets
train_dataset = load_from_disk('train_dataset')
test_dataset = load_from_disk('test_dataset')

# Define a model with a regression head for generating sentiment scores
class BertForSentimentRegression(BertForSequenceClassification):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = 1  # Sentiment score is a single continuous value
        self.classifier = torch.nn.Linear(config.hidden_size, 1)
    
    def forward(self, input_ids=None, attention_mask=None, labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss_fct = torch.nn.MSELoss()  # Mean Squared Error loss for regression
            loss = loss_fct(logits.view(-1), labels.view(-1))
        return SequenceClassifierOutput(loss=loss, logits=logits)

# Load the model
model = BertForSentimentRegression.from_pretrained('bert-base-uncased')

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    eval_strategy='steps',
    eval_steps=50,
    save_steps=100,
    save_total_limit=2,
    gradient_accumulation_steps=1,  # Ensure this is set
    fp16=False,
    no_cuda=False
)

print(f'Training arguments: {training_args}')

# Define custom Trainer
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'], labels=labels)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

    def training_step(self, model, inputs):
        model.train()
        inputs = self._prepare_inputs(inputs)
        loss = self.compute_loss(model, inputs)
        # Ensure gradient_accumulation_steps is not None
        gradient_accumulation_steps = self.args.gradient_accumulation_steps or 1
        if loss is None:
            raise ValueError("Loss is None. Ensure that the inputs include labels and are properly formatted.")
        loss = loss / gradient_accumulation_steps
        self.accelerator.backward(loss)
        return loss.detach()

# Initialize Trainer
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained('finetuned_model')
