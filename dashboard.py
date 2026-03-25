import streamlit as st
import requests

st.title("Gold prices from 3 different institutions")
API_URL = "https://just-basic-gold-tracking.onrender.com"

# 1. Add a spinner so users know it might take a moment to wake up the Render server
with st.spinner("Fetching live gold prices... (This may take up to a minute if the server is waking up)"):
    try:
        # 2. Add a long timeout to account for Render's free tier cold start
        response = requests.get(API_URL, timeout=60)
        response.raise_for_status() # Catches 404, 500, or 503 errors
        data = response.json()

        prices = data.get("prices", {})
        
        for bank, info in prices.items():
            st.subheader(bank)
            # .get() prevents KeyError if the data structure changes slightly
            st.write("Selling:", info.get("selling", "N/A"))
            st.write("Buying:", info.get("buying", "N/A"))
            st.write("Last Updated:", info.get("time", "N/A"))
            
        st.divider()

        # 3. Safely check if analysis is a dictionary (successful scrape) or a string (failed scrape)
        analysis = data.get("analysis")
        if isinstance(analysis, dict):
            st.success(f"Best place to BUY: {analysis.get('best_buy')}")
            st.success(f"Best place to SELL: {analysis.get('best_sell')}")
        elif isinstance(analysis, str):
            st.warning(analysis) # This will print "No valid data available" if scraping fails

    except requests.exceptions.Timeout:
        st.error("The API server took too long to respond. It might be waking up. Please refresh the page in a minute!")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the API. Error: {e}")