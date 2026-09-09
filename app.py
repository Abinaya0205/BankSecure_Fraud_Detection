import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from fraud_detector import FraudDetector
from data_generator import generate_sample_data

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="BankSecure - Fraud Analysis",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== THEME SETUP ====================
if 'theme' not in st.session_state:
    st.session_state.theme = "☀️ Light Mode"

def apply_theme(theme):
    if theme == "🌙 Dark Mode":
        bg_color = "#1e1e1e"
        text_color = "#ffffff"
        card_bg = "#2d2d2d"
        border_color = "#64b5f6"
        header_color = "#64b5f6"
        sidebar_bg = "#252525"
    else:
        bg_color = "#ffffff"
        text_color = "#000000"
        card_bg = "#f8f9fa"
        border_color = "#1a237e"
        header_color = "#1a237e"
        sidebar_bg = "#f0f2f6"
    
    return f"""
    <style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {header_color};
        text-align: center;
        padding: 1rem;
        border-bottom: 3px solid {border_color};
        margin-bottom: 2rem;
    }}
    .fraud-box {{
        background-color: #ffebee;
        border-left: 5px solid #e74c3c;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }}
    .legit-box {{
        background-color: #e8f5e9;
        border-left: 5px solid #2ecc71;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }}
    .metric-card {{
        background-color: {card_bg};
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: {text_color};
    }}
    .risk-high {{
        color: #e74c3c;
        font-weight: bold;
    }}
    .risk-medium {{
        color: #f39c12;
        font-weight: bold;
    }}
    .risk-low {{
        color: #2ecc71;
        font-weight: bold;
    }}
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stRadio label {{
        color: {text_color};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color};
    }}
    .sidebar-title {{
        text-align: center;
        padding: 10px;
    }}
    .sidebar-title h1 {{
        color: {header_color};
        font-size: 2rem;
        margin: 0;
    }}
    .sidebar-title p {{
        color: #888;
        font-size: 0.9rem;
        margin: 0;
    }}
    </style>
    """

st.markdown(apply_theme(st.session_state.theme), unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'detector' not in st.session_state:
    st.session_state.detector = FraudDetector()
if 'df' not in st.session_state:
    st.session_state.df = None
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # Set False for login

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-title">
            <h1>🏦 BankSecure</h1>
            <p>Fraud Analysis System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "📌 Navigation",
        ["📊 Dashboard", "🔍 Check Transaction", "📁 Batch Upload", "🤖 Train Model", "📈 Analytics"]
    )
    
    st.markdown("---")
    
    # Theme Toggle
    st.subheader("🎨 Theme")
    theme = st.radio(
        "Select Theme",
        ["☀️ Light Mode", "🌙 Dark Mode"],
        index=0 if st.session_state.theme == "☀️ Light Mode" else 1
    )
    
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()
    
    st.markdown("---")
    
    # Auto-Refresh Feature
    st.subheader("🔄 Auto-Refresh")
    auto_refresh = st.checkbox("Enable auto-refresh", value=st.session_state.auto_refresh)
    
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        st.rerun()
    
    if st.session_state.auto_refresh:
        refresh_interval = st.slider("Refresh every (seconds)", 5, 30, 10)
        st.caption(f"⏳ Refreshing every {refresh_interval} seconds")
    
    st.markdown("---")
    st.caption("🔒 AI-Powered Fraud Detection")
    
    # User info
    st.markdown("---")
    st.write(f"👤 Logged in as: Admin")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ==================== AUTO-REFRESH LOGIC ====================
if st.session_state.auto_refresh and page == "📊 Dashboard":
    time.sleep(refresh_interval)
    st.rerun()

# ==================== PAGE 1: DASHBOARD ====================
if page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Fraud Detection Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📥 Generate Sample Data", use_container_width=True):
            with st.spinner("Generating data..."):
                st.session_state.df = generate_sample_data(1000)
                st.success("✅ Sample data generated!")
        
        uploaded_file = st.file_uploader("Or upload CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success("✅ Data uploaded!")
    
    with col2:
        if st.session_state.df is not None:
            df = st.session_state.df
            st.info(f"""
            **📊 Data Summary**
            - Total: {len(df)}
            - Fraud: {df['is_fraud'].sum()}
            - Rate: {df['is_fraud'].mean()*100:.2f}%
            """)
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h5>Total</h5><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h5>Fraud</h5><h2 style="color:#e74c3c">{df["is_fraud"].sum()}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h5>Fraud Rate</h5><h2 style="color:#e74c3c">{df["is_fraud"].mean()*100:.1f}%</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h5>Avg Amount</h5><h2>₹{df["amount"].mean():,.0f}</h2></div>', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fraud_counts = df['is_fraud'].value_counts().reset_index()
            fraud_counts.columns = ['Type', 'Count']
            fraud_counts['Type'] = fraud_counts['Type'].map({0: 'Legit', 1: 'Fraud'})
            fig = px.pie(fraud_counts, values='Count', names='Type', 
                        title='Transaction Distribution',
                        color='Type',
                        color_discrete_map={'Legit': '#2ecc71', 'Fraud': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            legit = df[df['is_fraud']==0]
            fraud = df[df['is_fraud']==1]
            fig.add_trace(go.Histogram(x=legit['amount'], name='Legit', marker_color='#2ecc71', opacity=0.7))
            fig.add_trace(go.Histogram(x=fraud['amount'], name='Fraud', marker_color='#e74c3c', opacity=0.7))
            fig.update_layout(title='Amount Distribution', barmode='overlay')
            st.plotly_chart(fig, use_container_width=True)
        
        # Suspicious transactions
        st.markdown("---")
        st.subheader("🔍 Suspicious Transactions")
        
        suspicious = df[df['is_fraud'] == 1].head(20)
        if len(suspicious) > 0:
            st.dataframe(
                suspicious[['transaction_id', 'user_id', 'amount', 'merchant', 'location', 'hour']], 
                use_container_width=True
            )
        else:
            st.info("✅ No suspicious transactions found!")

        st.markdown("---")
        # PDF Report Button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                try:
                    from report_generator import generate_simple_report
                    import io
                    
                    with st.spinner("Generating report..."):
                        pdf = generate_simple_report(df)
                        pdf_output = io.BytesIO()
                        pdf.output(pdf_output, 'F')
                        pdf_output.seek(0)
                    
                        st.download_button(
                            label="📥 Download Report",
                            data=pdf_output,
                            file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                except Exception as e:
                    st.warning(f"⚠️ PDF Error: {e}")
# ==================== PAGE 2: CHECK TRANSACTION ====================
elif page == "🔍 Check Transaction":
    st.markdown('<div class="main-header">🔍 Check Single Transaction</div>', unsafe_allow_html=True)
    
    if not st.session_state.model_trained:
        st.warning("⚠️ Model not trained! Go to '🤖 Train Model' page first.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Enter Transaction Details")
        
        amount = st.number_input("Amount (₹)", min_value=1.0, value=10000.0, step=100.0)
        
        merchant = st.selectbox("Merchant", [
            "Amazon", "Flipkart", "Tanishq", "Malabar Gold", "Crypto Exchange",
            "Petrol Pump", "Swiggy", "Zomato", "Travel", "Electronics"
        ])
        
        merchant_risk_map = {
            "Amazon": 15, "Flipkart": 15, "Tanishq": 40, "Malabar Gold": 45,
            "Crypto Exchange": 55, "Petrol Pump": 10, "Swiggy": 10,
            "Zomato": 10, "Travel": 15, "Electronics": 20
        }
        merchant_risk = merchant_risk_map.get(merchant, 15)
        
        hour = st.slider("Hour of Transaction", 0, 23, 14)
        is_new_device = st.selectbox("Is this a new device?", ["No", "Yes"])
        prev_txns = st.number_input("Previous transactions by this user", min_value=0, value=20)
        location = st.selectbox("Location", ["India", "International"])
    
    with col2:
        st.subheader("📊 Prediction Result")
        
        if st.button("🔮 Predict", use_container_width=True):
            transaction = {
                'amount': amount,
                'merchant_risk': merchant_risk,
                'hour': hour,
                'is_new_device': 1 if is_new_device == "Yes" else 0,
                'prev_transactions': prev_txns,
                'location': location
            }
            
            rule_score, reasons = st.session_state.detector.get_rule_based_score(transaction)
            ml_result = st.session_state.detector.predict(transaction)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("ML Prediction", ml_result['prediction'])
                st.metric("Confidence", f"{ml_result['confidence']*100:.1f}%")
                st.metric("Fraud Probability", f"{ml_result['probability']*100:.1f}%")
            
            with col_b:
                st.metric("Rule-Based Score", f"{rule_score}/100")
                
                if rule_score < 30:
                    risk_text = "LOW 🟢"
                    risk_class = "risk-low"
                elif rule_score < 60:
                    risk_text = "MEDIUM 🟡"
                    risk_class = "risk-medium"
                else:
                    risk_text = "HIGH 🔴"
                    risk_class = "risk-high"
                
                st.markdown(f"**Risk Level:** <span class='{risk_class}'>{risk_text}</span>", unsafe_allow_html=True)
                
                if reasons:
                    st.write("**Rules Triggered:**")
                    for r in reasons:
                        st.write(f"• {r}")
            
            if ml_result['prediction'] == 'FRAUD' or rule_score > 50:
                st.markdown(f"""
                    <div class="fraud-box">
                        🚨 <b>FRAUD ALERT!</b><br>
                        Probability: {ml_result['probability']*100:.1f}%<br>
                        Risk Score: {rule_score}/100
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="legit-box">
                        ✅ <b>Transaction appears legitimate</b><br>
                        Probability: {ml_result['probability']*100:.1f}%<br>
                        Risk Score: {rule_score}/100
                    </div>
                """, unsafe_allow_html=True)

# ==================== PAGE 3: BATCH UPLOAD ====================
elif page == "📁 Batch Upload":
    st.markdown('<div class="main-header">📁 Batch Upload & Process</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("**Preview:**")
        st.dataframe(df.head(), use_container_width=True)
        
        if st.button("🚀 Process All Transactions"):
            with st.spinner("Processing..."):
                try:
                    required = ['amount', 'merchant_risk', 'hour', 'is_new_device', 'prev_transactions']
                    missing = [col for col in required if col not in df.columns]
                    
                    if missing:
                        st.error(f"Missing columns: {missing}")
                    else:
                        result_df = st.session_state.detector.predict_batch(df)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", len(result_df))
                        with col2:
                            fraud_count = len(result_df[result_df['prediction'] == 'FRAUD'])
                            st.metric("Fraud Detected", fraud_count)
                        with col3:
                            st.metric("Fraud Rate", f"{fraud_count/len(result_df)*100:.1f}%")
                        
                        st.subheader("🔍 Suspicious Transactions")
                        suspicious = result_df[result_df['prediction'] == 'FRAUD']
                        if len(suspicious) > 0:
                            st.dataframe(suspicious, use_container_width=True)
                            
                            csv = suspicious.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Suspicious List (CSV)",
                                data=csv,
                                file_name="suspicious_transactions.csv",
                                mime="text/csv"
                            )
                        else:
                            st.success("✅ No suspicious transactions found!")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== PAGE 4: TRAIN MODEL ====================
elif page == "🤖 Train Model":
    st.markdown('<div class="main-header">🤖 Train ML Model</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.df is not None:
            df = st.session_state.df
            st.write(f"**Dataset:** {len(df)} transactions")
            st.write(f"**Fraud Rate:** {df['is_fraud'].mean()*100:.2f}%")
            
            if st.button("🎯 Train Now", use_container_width=True):
                with st.spinner("Training model..."):
                    try:
                        result = st.session_state.detector.train(df)
                        st.session_state.model_trained = True
                        
                        st.success("✅ Model trained successfully!")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Train Accuracy", f"{result['train_accuracy']*100:.1f}%")
                        with col_b:
                            st.metric("Test Accuracy", f"{result['test_accuracy']*100:.1f}%")
                            
                        importance = pd.DataFrame({
                            'Feature': ['Amount', 'Merchant Risk', 'Hour', 'New Device', 'History'],
                            'Importance': [0.35, 0.25, 0.15, 0.15, 0.10]
                        })
                        fig = px.bar(importance, x='Importance', y='Feature', 
                                   title='Feature Importance',
                                   color='Importance',
                                   color_continuous_scale='Blues')
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Training failed: {str(e)}")
        else:
            st.info("No data available. Generate or upload data first.")
    
    with col2:
        st.subheader("📌 Model Status")
        if st.session_state.model_trained:
            st.success("✅ Model is ready!")
            st.info("""
            **Features Used:**
            - Amount
            - Merchant Risk
            - Time
            - New Device
            - Transaction History
            
            **Algorithm:** Random Forest
            """)
        else:
            st.warning("⚠️ Not trained yet")

# ==================== PAGE 5: ANALYTICS ====================
else:
    st.markdown('<div class="main-header">📈 Analytics & Insights</div>', unsafe_allow_html=True)
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        col1, col2 = st.columns(2)
        with col1:
            min_amt = st.number_input("Min Amount", 0, 100000, 0)
        with col2:
            max_amt = st.number_input("Max Amount", 0, 500000, 200000)
        
        filtered = df[(df['amount'] >= min_amt) & (df['amount'] <= max_amt)]
        st.write(f"Showing {len(filtered)} transactions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hourly = filtered[filtered['is_fraud']==1].groupby('hour').size().reset_index()
            hourly.columns = ['Hour', 'Count']
            fig = px.bar(hourly, x='Hour', y='Count', title='Fraud by Hour',
                        color='Count', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            merchant = filtered.groupby('merchant').agg({
                'is_fraud': 'mean',
                'transaction_id': 'count'
            }).reset_index()
            merchant.columns = ['Merchant', 'Fraud Rate', 'Count']
            merchant['Fraud Rate'] = merchant['Fraud Rate'] * 100
            merchant = merchant.sort_values('Fraud Rate', ascending=False).head(10)
            fig = px.bar(merchant, x='Fraud Rate', y='Merchant', 
                        title='Risk by Merchant', orientation='h',
                        color='Fraud Rate', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        fig = px.box(filtered, x='is_fraud', y='amount', 
                    title='Amount Distribution by Fraud Status',
                    labels={'is_fraud': 'Type', 'amount': 'Amount (₹)'})
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Legit', 'Fraud']
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No data available. Please generate or upload data.")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🏦 BankSecure Fraud Detection System | Powered by Machine Learning
    </div>
""", unsafe_allow_html=True)