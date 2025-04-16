
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Equity Dashboard", layout="wide")

st.title("Equity Research Dashboard")
ticker = st.text_input("Enter NSE/BSE Stock Symbol (e.g., INFY.NS, TCS.NS)", "INFY.NS")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        st.subheader("Company Overview")
        st.write(f"**Name:** {info.get('longName', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Website:** {info.get('website', 'N/A')}")

        st.subheader("1-Year Stock Price")
        st.line_chart(hist["Close"])

    except Exception as e:
        st.error(f"Error fetching data: {e}")
