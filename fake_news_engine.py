import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import streamlit as st
import torch.nn.functional as F

# Load a Pre-trained Fake News Detection Model
# We use 'mrm8488/bert-tiny-finetuned-fake-news-detection' 
# It is fast, lightweight, and accurate for this purpose.
@st.cache_resource
def load_fake_news_model():
    model_name = "mrm8488/bert-tiny-finetuned-fake-news-detection"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model

def detect_fake_news(text):
    """
    Analyzes a headline and returns:
    - Label: 'REAL' or 'FAKE'
    - Confidence: Score (0.0 to 1.0)
    """
    tokenizer, model = load_fake_news_model()
    
    # 1. Prepare text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    # 2. Predict
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 3. Get Probabilities
    probs = F.softmax(outputs.logits, dim=1)
    
    # The model classes are usually [0: Fake, 1: Real] (Check model card if unsure)
    # For this specific model: Index 1 is Real, Index 0 is Fake
    fake_prob = probs[0][0].item()
    real_prob = probs[0][1].item()
    
    if real_prob > fake_prob:
        return "REAL", real_prob
    else:
        return "FAKE", fake_prob