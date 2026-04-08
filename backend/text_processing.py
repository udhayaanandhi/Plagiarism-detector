import re
import string

def read_file(filepath):
    """Read text from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def preprocess(text):
    """
    Normalize text:
    - Convert to lowercase
    - Remove punctuation and special characters
    - Collapse multiple spaces
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    """Split preprocessed text into word tokens."""
    return text.split()

def get_sentences(text):
    """Split raw text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def preprocess_file(filepath):
    """Read and preprocess a file, returning raw text, clean text, and tokens."""
    raw = read_file(filepath)
    clean = preprocess(raw)
    tokens = tokenize(clean)
    return raw, clean, tokens
