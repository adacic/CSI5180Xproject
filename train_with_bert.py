import json
import torch
import os
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load and preprocess the dataset
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)  # Load JSON directly
    except json.JSONDecodeError as e:
        print(f"Error loading JSON file: {e}")
        return []
    return data

def preprocess_data(data):
    commands = [item['command'] for item in data]
    intents = [item['intent'] for item in data]
    return commands, intents

# Ensure required dependencies are installed
try:
    from accelerate import Accelerator
except ImportError:
    raise ImportError("Using the `Trainer` with `PyTorch` requires `accelerate>=0.26.0`. "
                      "Please run `pip install transformers[torch]` or `pip install 'accelerate>=0.26.0'`.")

# Check if the model and tokenizer are already saved
model_dir = './intent_model'
if os.path.exists(model_dir):
    print("Loading the saved model and tokenizer...")
    model = RobertaForSequenceClassification.from_pretrained(model_dir)
    tokenizer = RobertaTokenizer.from_pretrained(model_dir)
    
    # Load id2label and label2id mappings
    id2label_path = os.path.join(model_dir, 'id2label.json')
    label2id_path = os.path.join(model_dir, 'label2id.json')
    if os.path.exists(id2label_path) and os.path.exists(label2id_path):
        with open(id2label_path, 'r') as f:
            id2label = json.load(f)
        with open(label2id_path, 'r') as f:
            label2id = json.load(f)
        print(f"Loaded id2label mapping: {id2label}")  # Debugging output
    else:
        print("id2label.json or label2id.json not found. Regenerating mappings from the dataset...")
        # Load dataset to regenerate mappings
        data = load_data('chatbot_commands_intents.json')
        _, intents = preprocess_data(data)
        labels = list(set(intents))
        label2id = {label: i for i, label in enumerate(labels)}
        id2label = {i: label for label, i in label2id.items()}
        
        # Save regenerated mappings
        with open(id2label_path, 'w') as f:
            json.dump(id2label, f)
        with open(label2id_path, 'w') as f:
            json.dump(label2id, f)
        print(f"Regenerated and saved id2label mapping: {id2label}")
else:
    print("Training the model as no saved model is found...")
    # Load dataset
    data = load_data('chatbot_commands_intents.json')
    commands, intents = preprocess_data(data)

    # Split the dataset into training and validation sets
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
    train_dataset = Dataset.from_dict({'command': [item['command'] for item in train_data], 'intent': [item['intent'] for item in train_data]})
    val_dataset = Dataset.from_dict({'command': [item['command'] for item in val_data], 'intent': [item['intent'] for item in val_data]})

    # Tokenize the datasets
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    def tokenize_function(examples):
        return tokenizer(examples['command'], padding="max_length", truncation=True)

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)

    # Encode the labels
    labels = list(set(intents))
    label2id = {label: i for i, label in enumerate(labels)}
    id2label = {i: label for label, i in label2id.items()}
    train_dataset = train_dataset.map(lambda x: {'label': label2id[x['intent']]})
    val_dataset = val_dataset.map(lambda x: {'label': label2id[x['intent']]})

    # Load pre-trained RoBERTa model
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=len(labels))

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=10,  # Increased from 5 to 10
        per_device_train_batch_size=8,  # Reduced batch size from 16 to 8
        warmup_steps=200,  # Reduced warmup steps from 300 to 200
        weight_decay=0.01,
        logging_dir='./logs',
        eval_strategy="steps",  # Updated from evaluation_strategy to eval_strategy
        eval_steps=50,  # Evaluate every 50 steps for more frequent feedback
        learning_rate=3e-5,  # Reduced learning rate from 5e-5 to 3e-5
        save_steps=500,  # Save model every 500 steps
        save_total_limit=2,  # Keep only the last 2 checkpoints
        load_best_model_at_end=True,  # Load the best model at the end of training
        seed=42,  # Set seed for reproducibility
        fp16=True  # Enable mixed precision training
    )

    # Trainer
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = torch.argmax(torch.tensor(logits), dim=-1)
        return {"accuracy": accuracy_score(labels, predictions)}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,  # Pass validation dataset
        compute_metrics=compute_metrics
    )

    # Train the model
    trainer.train()

    # Save the model and tokenizer
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    
    # Save id2label and label2id mappings
    id2label_path = os.path.join(model_dir, 'id2label.json')
    label2id_path = os.path.join(model_dir, 'label2id.json')
    with open(id2label_path, 'w') as f:
        json.dump(id2label, f)
    with open(label2id_path, 'w') as f:
        json.dump(label2id, f)

# Function to detect intent from user command
def detect_intent(command):
    inputs = tokenizer(command, return_tensors="pt", padding="max_length", truncation=True)
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1).item()
    print(f"Prediction index: {predictions}")  # Debugging output
    return id2label.get(str(predictions), "Unknown intent")  # Ensure predictions are converted to string

# New function to expose intent detection for external use
def get_intent(user_command):
    return detect_intent(user_command)