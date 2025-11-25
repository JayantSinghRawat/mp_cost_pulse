"""
Rent Listing Classifier using PyTorch DistilBERT
Classifies rent listings as "fair" or "overpriced" based on listing text and features
"""
import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from typing import Dict, List, Optional
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class RentClassifier:
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            # Initialize with pretrained model
            self.model = DistilBertForSequenceClassification.from_pretrained(
                'distilbert-base-uncased',
                num_labels=2  # fair vs overpriced
            )
            self.model.to(self.device)
            self.model.eval()
    
    def prepare_text_features(self, listing: Dict) -> str:
        """Prepare text input from listing data"""
        # Combine title, description, and key features
        text_parts = []
        
        if listing.get('title'):
            text_parts.append(listing['title'])
        
        if listing.get('description'):
            text_parts.append(listing['description'])
        
        # Add structured features as text
        features = []
        if listing.get('property_type'):
            features.append(f"Property type: {listing['property_type']}")
        if listing.get('area_sqft'):
            features.append(f"Area: {listing['area_sqft']} sqft")
        if listing.get('furnished'):
            features.append(f"Furnishing: {listing['furnished']}")
        
        text = ' '.join(text_parts)
        if features:
            text += ' ' + ' '.join(features)
        
        return text
    
    def classify(self, listing: Dict, locality_avg_rent: Optional[float] = None) -> Dict:
        """Classify a rent listing as fair or overpriced"""
        # Prepare text
        text = self.prepare_text_features(listing)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        ).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
        
        # Get predicted class and confidence
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_class].item()
        
        # Compare with locality average if available
        price_comparison = None
        if locality_avg_rent and listing.get('rent_amount'):
            rent_amount = listing['rent_amount']
            diff_percent = ((rent_amount - locality_avg_rent) / locality_avg_rent) * 100
            price_comparison = {
                'listing_rent': float(rent_amount),
                'locality_avg': float(locality_avg_rent),
                'difference_percent': float(diff_percent)
            }
        
        result = {
            'classification': 'fair' if predicted_class == 0 else 'overpriced',
            'confidence': float(confidence),
            'probabilities': {
                'fair': float(probabilities[0][0].item()),
                'overpriced': float(probabilities[0][1].item())
            },
            'price_comparison': price_comparison
        }
        
        return result
    
    def train(self, training_data: List[Dict], labels: List[int], epochs: int = 3):
        """Fine-tune the model on training data"""
        logger.info("Training rent classifier model...")
        
        # This is a simplified training - full implementation would include
        # proper data loading, batching, optimization, etc.
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        
        # Tokenize all texts
        texts = [self.prepare_text_features(item) for item in training_data]
        encoded = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        ).to(self.device)
        
        labels_tensor = torch.tensor(labels).to(self.device)
        
        # Training loop (simplified)
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(**encoded, labels=labels_tensor)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        
        self.model.eval()
        logger.info("Model training completed")
    
    def save_model(self, model_path: str):
        """Save the fine-tuned model"""
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a fine-tuned model"""
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        logger.info(f"Model loaded from {model_path}")

