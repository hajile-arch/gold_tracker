import streamlit as st
import requests

st.title("Gold price from 3 different instituitions")
API_URL = "http://127.0.0.1:10000"
response = requests.get(API_URL)
data = response.json()

prices = data["prices"]
for bank, info in prices.items():
    st.subheader(bank)
    st.write("Selling:", info["selling"])
    st.write("Buying:", info["buying"])
    st.write("Last Updated:", info["time"])
    
st.divider()

if "analysis" in data:
    st.success(f"Best place to BUY: {data['analysis']['best_buy']}")
    st.success(f"Best place to SELL: {data['analysis']['best_sell']}")
    
