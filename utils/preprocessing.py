import re
import string
import pandas as pd
from bs4 import BeautifulSoup

def clean_text(text):
    """
    Cleans the input text by removing URLs, HTML tags, special characters, and converting to lowercase.
    """
    if not isinstance(text, str):
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove square brackets and their contents
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove punctuation
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    
    # Remove newlines
    text = re.sub(r'\n', ' ', text)
    
    # Remove words containing numbers
    text = re.sub(r'\w*\d\w*', '', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_and_balance_data(fake_df, true_df, max_samples_per_class=20000):
    """
    Preprocesses the datasets, removes duplicates, balances them, and merges them.
    """
    # Add labels (0 for Fake, 1 for True)
    fake_df['label'] = 0
    true_df['label'] = 1
    
    # Combine title and text for better context
    fake_df['content'] = fake_df['title'] + " " + fake_df['text']
    true_df['content'] = true_df['title'] + " " + true_df['text']
    
    # Keep only relevant columns
    fake_df = fake_df[['content', 'label']]
    true_df = true_df[['content', 'label']]
    
    # Drop duplicates
    fake_df = fake_df.drop_duplicates()
    true_df = true_df.drop_duplicates()
    
    # Clean text (can be slow, sample first if dataset is too large, but doing it thoroughly is better)
    # We will balance first to save time on cleaning
    min_len = min(len(fake_df), len(true_df), max_samples_per_class)
    
    fake_df = fake_df.sample(min_len, random_state=42)
    true_df = true_df.sample(min_len, random_state=42)
    
    # Merge datasets
    df = pd.concat([fake_df, true_df], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Clean the content column
    print("Cleaning text data... this may take a moment.")
    df['clean_content'] = df['content'].apply(clean_text)
    
    # Drop rows that became empty after cleaning
    df = df[df['clean_content'].str.strip() != '']
    
    return df
