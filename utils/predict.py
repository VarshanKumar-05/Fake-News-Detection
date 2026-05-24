import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import re
from .preprocessing import clean_text
import os

# Define paths robustly for Docker and Local compatibility
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models", "saved_model")

# Sensational/Suspicious lexicon for lightweight highlighting
SUSPICIOUS_WORDS = set([
    "shocking", "scandal", "hoax", "conspiracy", "secret", "truth", "exposed",
    "banned", "deleted", "miracle", "cure", "urgent", "breaking", "bombshell",
    "must read", "you won't believe", "mind blowing", "coverup", "deep state",
    "fake", "fraud", "scam", "rumor", "leak", "leaked", "insider", "whistleblower",
    "unbelievable", "censored"
])

class FakeNewsPredictor:
    def __init__(self, model_path=MODEL_DIR):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # --- DEBUG LOGGING ---
        print("\n" + "="*50, flush=True)
        print(f"DEBUG: Current working directory: {os.getcwd()}", flush=True)
        print(f"DEBUG: Absolute model path expected: {model_path}", flush=True)
        print(f"DEBUG: Does model path exist? {os.path.exists(model_path)}", flush=True)
        
        if os.path.exists(model_path):
            print(f"DEBUG: Files in model path: {os.listdir(model_path)}", flush=True)
        else:
            print("DEBUG: WARNING! Model directory is MISSING! Check Dockerfile COPY command and .dockerignore.", flush=True)
        print("="*50 + "\n", flush=True)
        
        try:
            self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
            self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
            
            # Apply dynamic quantization for ultra-fast CPU inference
            if self.device.type == 'cpu':
                print("Applying dynamic quantization to model for faster CPU inference...", flush=True)
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
                
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            print("DEBUG: Model loaded successfully!", flush=True)
        except Exception as e:
            print(f"DEBUG: Error loading model from {model_path}. Error: {e}", flush=True)
            self.is_loaded = False
            
    def predict(self, text):
        if not self.is_loaded:
            return {"error": "Model not loaded. Train the model first."}
            
        cleaned_text = clean_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt"
        )
        
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
        # Class 0: Fake, Class 1: True
        fake_prob = probabilities[0][0].item()
        true_prob = probabilities[0][1].item()
        
        is_fake = fake_prob > true_prob
        confidence = fake_prob if is_fake else true_prob
        
        # Identify suspicious keywords for lightweight explanation
        words = re.findall(r'\b\w+\b', cleaned_text.lower())
        found_suspicious = [word for word in words if word in SUSPICIOUS_WORDS]
        
        # Generate Reasoning
        if is_fake:
            if len(found_suspicious) > 2:
                reason = "Highly sensational language and exaggerated claims detected indicating potential misinformation."
            elif len(found_suspicious) > 0:
                reason = "Suspicious keywords found along with unreliable narrative patterns typical of fake news."
            else:
                reason = "The structural patterns and sentiment of the text strongly match known characteristics of fabricated news."
        else:
            if len(found_suspicious) > 0:
                reason = "Despite some sensational words, the overall structure maintains neutral journalistic integrity."
            elif confidence > 0.90:
                reason = "Strongly neutral journalistic language, objective tone, and reliable reporting patterns detected."
            else:
                reason = "Text follows reliable factual reporting patterns with an objective narrative."
                
        return {
            "prediction": "Fake News" if is_fake else "Real News",
            "confidence": confidence,
            "fake_probability": fake_prob,
            "true_probability": true_prob,
            "suspicious_keywords": list(set(found_suspicious)),
            "cleaned_text": cleaned_text,
            "reasoning": reason
        }
