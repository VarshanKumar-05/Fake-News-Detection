import os
import torch
import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
from utils.preprocessing import preprocess_and_balance_data

# Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models", "saved_model")
FAKE_CSV = os.path.join(DATA_DIR, "Fake.csv")
TRUE_CSV = os.path.join(DATA_DIR, "True.csv")

BATCH_SIZE = 16
EPOCHS = 3
MAX_LEN = 256
LEARNING_RATE = 2e-5

class NewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def main():
    print("Starting Training Pipeline...")
    
    # 1. Load Data
    if not os.path.exists(FAKE_CSV) or not os.path.exists(TRUE_CSV):
        print(f"Error: {FAKE_CSV} or {TRUE_CSV} not found.")
        print("Please place the dataset files in the 'data' folder.")
        return

    print("Loading datasets...")
    fake_df = pd.read_csv(FAKE_CSV)
    true_df = pd.read_csv(TRUE_CSV)

    # 2. Preprocess
    print("Preprocessing and balancing datasets...")
    df = preprocess_and_balance_data(fake_df, true_df, max_samples_per_class=5000) # Increased to 5k for high accuracy
    
    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        df['clean_content'].values,
        df['label'].values,
        test_size=0.2,
        random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # 4. Tokenization
    print("Loading DistilBERT tokenizer...")
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

    train_dataset = NewsDataset(X_train, y_train, tokenizer, MAX_LEN)
    test_dataset = NewsDataset(X_test, y_test, tokenizer, MAX_LEN)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 5. Model Loading
    print("Loading DistilBERT model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2
    )
    model = model.to(device)

    # 6. Optimizer, Scheduler, and Scaler
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )
    
    scaler = torch.amp.GradScaler('cuda') if torch.cuda.is_available() else None
    
    # 7. Training Loop
    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")
        print("-" * 10)
        
        model.train()
        train_losses = []
        
        for i, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            optimizer.zero_grad()
            
            if scaler is not None:
                with torch.amp.autocast('cuda'):
                    outputs = model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    loss = outputs.loss
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                
            scheduler.step()
            train_losses.append(loss.item())
            
            if (i + 1) % 50 == 0:
                print(f"Batch {i + 1}/{len(train_loader)} - Loss: {np.mean(train_losses):.4f}")

        # 8. Evaluation
        model.eval()
        val_losses = []
        predictions = []
        true_labels = []

        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                val_losses.append(loss.item())

                logits = outputs.logits
                _, preds = torch.max(logits, dim=1)

                predictions.extend(preds.cpu().tolist())
                true_labels.extend(labels.cpu().tolist())

        val_acc = accuracy_score(true_labels, predictions)
        print(f"Validation Loss: {np.mean(val_losses):.4f}")
        print(f"Validation Accuracy: {val_acc:.4f}")

    # 9. Final Metrics & Save
    print("\nClassification Report:")
    print(classification_report(true_labels, predictions, target_names=["Fake", "True"]))

    print(f"\nSaving model to {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print("Training complete!")

if __name__ == "__main__":
    main()
