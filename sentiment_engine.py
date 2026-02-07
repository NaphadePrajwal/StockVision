import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import streamlit as st
import torch.nn.functional as F

# Load FinBERT from Hugging Face
# We use st.cache_resource so we only download the model ONCE, not every time you click a button.
@st.cache_resource
def load_finbert():
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model

def predict_finbert_sentiment(text_list):
    """
    Runs FinBERT on a list of headlines.
    Returns: List of probabilities for [Positive, Negative, Neutral]
    """
    tokenizer, model = load_finbert()
    
    inputs = tokenizer(text_list, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Convert logits to probabilities (0 to 1)
    probabilities = F.softmax(outputs.logits, dim=1)
    return probabilities