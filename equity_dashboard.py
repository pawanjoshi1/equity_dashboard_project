import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="Equity Research Dashboard")

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")
    return info, hist

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

def display_overview(info, hist):
    st.header(f"{info.get('shortName', '')} ({info.get('symbol', '')})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sector", info.get("sector", "N/A"))
    col2.metric("Industry", info.get("industry", "N/A"))
    col3.metric("Market Cap", f"{info.get('marketCap', 0)/1e9:.2f} B")

    st.write("**Company Website:**", info.get("website", "N/A"))
    st.write("**Headquarters:**", info.get("city", "") + ", " + info.get("country", ""))
    st.line_chart(hist['Close'])

def display_management(info):
    st.subheader("Management")
    st.write(info.get("companyOfficers", "No data available"))

def display_history(info):
    st.subheader("Company History")
    st.write(info.get("longBusinessSummary", "No history found."))

def display_financials(ticker):
    st.subheader("Quarterly Financials")
    fin = get_financials(ticker)
    st.dataframe(fin)

def display_product_details(info):
    st.subheader("Product Revenue Breakdown")
    st.write("Detailed product revenue breakdown may not be available for all companies.")
    st.write(info.get("longBusinessSummary", "No data available."))

def display_orders(ticker):
    st.subheader("Recent Orders")
    st.write("Fetching latest contracts/orders from news...")
    orders = get_news(f"{ticker} order received", 6)
    for link in orders:
        st.markdown(f"- [Order News]({link})")

def display_news(ticker, sector):
    st.subheader("Company News")
    news = get_news(ticker, 6)
    for link in news:
        st.markdown(f"- [Company News]({link})")

    st.subheader("Sector News")
    if sector != "N/A":
        sector_news = get_news(sector + " sector", 1)
        for link in sector_news:
            st.markdown(f"- [Sector News]({link})")

def main():
    st.title("Equity Research Dashboard")
    ticker = st.text_input("Enter NSE/BSE Stock Symbol (e.g. INFY.NS or TCS.BO)", "INFY.NS")

    if ticker:
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
