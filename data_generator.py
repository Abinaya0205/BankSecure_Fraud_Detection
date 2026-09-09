import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_sample_data(n=1000):
    """Generate fake transaction data"""
    transactions = []
    users = [f'U_{i:04d}' for i in range(1, 101)]
    
    merchants = {
        'Amazon': 15, 'Flipkart': 15, 'Swiggy': 10, 'Zomato': 10,
        'Tanishq': 40, 'Malabar Gold': 45, 'Petrol Pump': 10,
        'Crypto Exchange': 55, 'Insurance': 12, 'Education': 8,
        'Travel': 15, 'Electronics': 20, 'Grocery': 5, 'Restaurant': 8
    }
    
    for i in range(n):
        user = random.choice(users)
        is_fraud = 1 if random.random() < 0.03 else 0
        
        if is_fraud:
            amount = np.random.uniform(50000, 200000)
            hour = np.random.choice([0,1,2,3,4,23])
            is_new_device = 1 if random.random() < 0.7 else 0
            location = 'India' if random.random() < 0.3 else 'International'
        else:
            amount = np.random.uniform(100, 40000)
            hour = np.random.randint(6, 22)
            is_new_device = 1 if random.random() < 0.1 else 0
            location = 'India' if random.random() < 0.9 else 'International'
        
        merchant = random.choice(list(merchants.keys()))
        merchant_risk = merchants[merchant]
        prev_transactions = random.randint(0, 50) if not is_fraud else random.randint(0, 10)
        
        transaction = {
            'transaction_id': f'TXN_{i:06d}',
            'user_id': user,
            'amount': round(amount, 2),
            'merchant': merchant,
            'merchant_risk': merchant_risk,
            'location': location,
            'hour': hour,
            'is_new_device': is_new_device,
            'prev_transactions': prev_transactions,
            'is_fraud': is_fraud
        }
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)

# Generate and save sample data
if __name__ == "__main__":
    df = generate_sample_data(1000)
    df.to_csv('sample_transactions.csv', index=False)
    print(f"✅ Generated {len(df)} sample transactions")
    print(f"📊 Fraud rate: {df['is_fraud'].mean()*100:.2f}%")