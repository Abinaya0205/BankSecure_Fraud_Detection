import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class FraudDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        
    def prepare_data(self, df):
        """Prepare data for ML model"""
        df = df.copy()
        df['amount_log'] = np.log1p(df['amount'])
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        X = df[['amount', 'amount_log', 'merchant_risk', 'hour_sin', 'hour_cos', 
                'is_new_device', 'prev_transactions']]
        return X
    
    def train(self, df):
        """Train the model"""
        try:
            X = self.prepare_data(df)
            y = df['is_fraud']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            self.is_trained = True
            
            # Save model
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, 'models/fraud_model.pkl')
            joblib.dump(self.scaler, 'models/scaler.pkl')
            
            return {
                'train_accuracy': self.model.score(X_train_scaled, y_train),
                'test_accuracy': self.model.score(X_test_scaled, y_test),
                'n_samples': len(df),
                'fraud_rate': y.mean() * 100
            }
        except Exception as e:
            raise Exception(f"Training failed: {str(e)}")
    
    def load_model(self):
        """Load saved model"""
        try:
            if os.path.exists('models/fraud_model.pkl') and os.path.exists('models/scaler.pkl'):
                self.model = joblib.load('models/fraud_model.pkl')
                self.scaler = joblib.load('models/scaler.pkl')
                self.is_trained = True
                return True
            return False
        except:
            return False
    
    def predict(self, transaction):
        """Predict single transaction"""
        # Try to load model if not trained
        if not self.is_trained:
            if not self.load_model():
                return {
                    'prediction': 'LEGIT',
                    'probability': 0.0,
                    'confidence': 1.0,
                    'error': 'Model not trained'
                }
        
        # Check if model exists
        if self.model is None or self.scaler is None:
            return {
                'prediction': 'LEGIT',
                'probability': 0.0,
                'confidence': 1.0,
                'error': 'Model not loaded'
            }
        
        try:
            features = np.array([[
                transaction['amount'],
                np.log1p(transaction['amount']),
                transaction['merchant_risk'],
                np.sin(2 * np.pi * transaction['hour'] / 24),
                np.cos(2 * np.pi * transaction['hour'] / 24),
                transaction['is_new_device'],
                transaction['prev_transactions']
            ]])
            
            features_scaled = self.scaler.transform(features)
            probability = self.model.predict_proba(features_scaled)[0, 1]
            prediction = self.model.predict(features_scaled)[0]
            
            return {
                'prediction': 'FRAUD' if prediction == 1 else 'LEGIT',
                'probability': probability,
                'confidence': max(probability, 1 - probability),
                'error': None
            }
        except Exception as e:
            return {
                'prediction': 'LEGIT',
                'probability': 0.0,
                'confidence': 1.0,
                'error': str(e)
            }
    
    def predict_batch(self, df):
        """Predict multiple transactions"""
        if not self.is_trained:
            self.load_model()
        
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Please train the model first.")
        
        try:
            df = df.copy()
            X = self.prepare_data(df)
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            
            df['prediction'] = ['FRAUD' if p == 1 else 'LEGIT' for p in predictions]
            df['fraud_probability'] = probabilities
            df['risk_level'] = df['fraud_probability'].apply(
                lambda x: 'HIGH' if x >= 0.7 else 'MEDIUM' if x >= 0.4 else 'LOW'
            )
            
            return df
        except Exception as e:
            raise Exception(f"Batch prediction failed: {str(e)}")
    
    def get_rule_based_score(self, transaction):
        """Calculate rule-based risk score"""
        score = 0
        reasons = []
        
        if transaction['amount'] > 100000:
            score += 30
            reasons.append("High amount > ₹1,00,000")
        elif transaction['amount'] > 50000:
            score += 20
            reasons.append("Amount > ₹50,000")
        
        if transaction['merchant_risk'] >= 40:
            score += 25
            reasons.append("High-risk merchant")
        elif transaction['merchant_risk'] >= 25:
            score += 15
            reasons.append("Medium-risk merchant")
        
        if transaction['hour'] in [0,1,2,3,4,5]:
            score += 20
            reasons.append("Late night transaction")
        
        if transaction['is_new_device'] == 1:
            score += 15
            reasons.append("New device used")
        
        if transaction['prev_transactions'] < 10:
            score += 10
            reasons.append("Limited transaction history")
        
        if transaction.get('location', 'India') != 'India':
            score += 10
            reasons.append("International transaction")
        
        return min(score, 100), reasons