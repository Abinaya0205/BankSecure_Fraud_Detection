from fpdf import FPDF
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'BankSecure - Fraud Report', 0, 1, 'C')
        self.cell(0, 5, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_simple_report(df):
    """Simple PDF report"""
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Fraud Detection Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Statistics
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Summary Statistics', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    total = len(df)
    fraud = df['is_fraud'].sum()
    fraud_rate = (fraud/total*100) if total > 0 else 0
    
    pdf.cell(0, 8, f'Total Transactions: {total}', 0, 1)
    pdf.cell(0, 8, f'Fraud Cases: {fraud}', 0, 1)
    pdf.cell(0, 8, f'Fraud Rate: {fraud_rate:.2f}%', 0, 1)
    pdf.cell(0, 8, f'Average Amount: ₹{df["amount"].mean():,.2f}', 0, 1)
    pdf.cell(0, 8, f'Max Amount: ₹{df["amount"].max():,.2f}', 0, 1)
    pdf.ln(5)
    
    # Suspicious transactions
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Top Suspicious Transactions', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    suspicious = df[df['is_fraud'] == 1].head(10)
    if len(suspicious) > 0:
        for _, row in suspicious.iterrows():
            pdf.cell(0, 6, f"ID: {row.get('transaction_id', 'N/A')} | Amount: ₹{row['amount']:,.2f} | Merchant: {row.get('merchant', 'Unknown')}", 0, 1)
    else:
        pdf.cell(0, 6, "No suspicious transactions found", 0, 1)
    
    return pdf