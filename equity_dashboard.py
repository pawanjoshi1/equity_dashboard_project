import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Equity Research Dashboard")

# --- Helper Functions ---
@st.cache_data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")
    return info, hist

@st.cache_data
def get_financials(ticker):
    stock = yf.Ticker(ticker)
    fin = stock.quarterly_financials
    return fin

def get_news(query, months_back=6, max_articles=5):
    today = datetime.today()
    date_filter = today - timedelta(days=30*months_back)
    url = f"https://news.google.com/search?q={query}%20after:{date_filter.date()}&hl=en-IN&gl=IN&ceid=IN:en"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    headlines = soup.select("article h3 a")[:max_articles]
    return [f"https://news.google.com{h['href'][1:]}" for h in headlines]

def format_large_number(num):
    if num is None:
        return "N/A"
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000.0:
            return f"{num:3.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}P"

def display_overview(info, hist):
    st.header(f"{info.get('shortName', '')} ({info.get('symbol', '')})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sector", info.get("sector", "N/A"))
    col2.metric("Industry", info.get("industry", "N/A"))
    col3.metric("Market Cap", format_large_number(info.get("marketCap", 0)))

    st.markdown(f"**Company Website:** [{info.get('website','N/A')}]({info.get('website','')})")
    st.markdown(f"**Headquarters:** {info.get('city','')} , {info.get('country','')}")
    st.plotly_chart(go.Figure(go.Scatter(x=hist.index, y=hist['Close'], name='Close Price')))

def display_management(info):
    st.subheader("Management")
    officers = info.get("companyOfficers", [])
    if officers:
        for officer in officers:
            with st.expander(officer.get("name", "Unknown")):
                st.write(f"**Role:** {officer.get('title', 'N/A')}")
                st.write(f"**Age:** {officer.get('age', 'N/A')}")
    else:
        st.write("No management data available.")

def display_history(info):
    st.subheader("Company History")
    st.write(info.get("longBusinessSummary", "No history found."))

def display_financials(ticker):
    st.subheader("Quarterly Financials")
    fin = get_financials(ticker)
    if fin.empty:
        st.warning("Financial data not available.")
        return

    st.dataframe(fin)

    try:
        rev = fin.loc["Total Revenue"]
        net = fin.loc["Net Income"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rev.index, y=rev.values, name="Revenue"))
        fig.add_trace(go.Bar(x=net.index, y=net.values, name="Net Income"))
        st.plotly_chart(fig)

        st.write("**YoY/QoQ Changes**")
        yoy_rev = rev.pct_change(periods=4).iloc[-1] * 100 if len(rev) >= 5 else None
        qoq_rev = rev.pct_change().iloc[-1] * 100 if len(rev) >= 2 else None
        st.metric("YoY Revenue Change", f"{yoy_rev:.2f}%" if yoy_rev else "N/A")
        st.metric("QoQ Revenue Change", f"{qoq_rev:.2f}%" if qoq_rev else "N/A")
    except Exception as e:
        st.error(f"Error creating financial charts: {e}")

def display_product_details(info):
    st.subheader("Product Revenue Breakdown")
    st.write("Detailed product revenue breakdown may not be available for all companies.")
    st.write(info.get("longBusinessSummary", "No data available."))

def display_orders(ticker):
    st.subheader("Recent Orders / Contracts")
    st.write("Fetching latest contracts/orders from news...")
    orders = get_news(f"{ticker} order received", 6)
    if orders:
        for i, link in enumerate(orders):
            st.markdown(f"{i+1}. [View Order News]({link})")
    else:
        st.write("No order news found.")

def display_news(ticker, sector):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Company News")
        news = get_news(ticker, 6)
        for link in news:
            st.markdown(f"- [Company News]({link})")

    with col2:
        st.subheader("Sector News")
        if sector != "N/A":
            sector_news = get_news(sector + " sector", 1)
            for link in sector_news:
                st.markdown(f"- [Sector News]({link})")

def main():
    st.title("Equity Research Dashboard")

    st.sidebar.title("Settings")
    theme = st.sidebar.radio("Theme", ["Light", "Dark"])
    favorites = ["INFY.NS", "TCS.BO", "RELIANCE.NS"]
    ticker = st.sidebar.selectbox("Select Stock", favorites)

    with st.spinner("Loading data..."):
        try:
            info, hist = get_stock_data(ticker)
            sector = info.get("sector", "N/A")

            tabs = st.tabs(["Overview", "Financials", "Orders", "News"])

            with tabs[0]:
                display_overview(info, hist)
                display_management(info)
                display_history(info)
                display_product_details(info)

            with tabs[1]:
                display_financials(ticker)

            with tabs[2]:
                display_orders(ticker)

            with tabs[3]:
                display_news(ticker, sector)

        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    main()
