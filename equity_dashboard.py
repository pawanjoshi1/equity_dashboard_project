import streamlit as st import yfinance as yf import pandas as pd import datetime from streamlit_option_menu import option_menu from plotly import graph_objs as go

st.set_page_config(page_title="Equity Research Dashboard", layout="wide")

--- HEADER ---

st.title("Equity Research Dashboard") st.markdown("Search and analyze detailed information about NSE & BSE stocks.")

--- STOCK SEARCH ---

stocks_df = pd.read_csv("https://archives.nseindia.com/content/equities/EQUITY_L.csv") stocks_df = stocks_df[['SYMBOL', 'NAME OF COMPANY']]

stocks_df['Display'] = stocks_df['SYMBOL'] + " - " + stocks_df['NAME OF COMPANY'] stock_choice = st.selectbox("Search for a Stock (NSE)", options=stocks_df['Display']) ticker = stock_choice.split(" - ")[0] + ".NS"

--- LOAD STOCK DATA ---

def load_stock_data(ticker): stock = yf.Ticker(ticker) info = stock.info hist = stock.history(period="1y") return info, hist

info, hist = load_stock_data(ticker)

--- COMPANY OVERVIEW ---

st.subheader(f"{info.get('longName', ticker)} - Overview") col1, col2, col3 = st.columns(3)

col1.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}") col2.metric("Sector", info.get('sector', 'N/A')) col3.metric("Industry", info.get('industry', 'N/A'))

st.markdown(f"Website: {info.get('website', '')}})")

--- STOCK PRICE CHART ---

st.subheader("Stock Price Chart") fig = go.Figure() fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close')) fig.update_layout(title="Closing Price", xaxis_title="Date", yaxis_title="Price") st.plotly_chart(fig, use_container_width=True)

--- FINANCIALS ---

st.subheader("Quarterly Financials") try: quarterly = yf.Ticker(ticker).quarterly_financials.T st.dataframe(quarterly) except: st.warning("Quarterly data not available")

--- COMPANY HISTORY ---

st.subheader("Company Description") st.markdown(info.get('longBusinessSummary', 'No description available'))

--- MANAGEMENT ---

st.subheader("Key Executives") if 'companyOfficers' in info: mgmt = pd.DataFrame(info['companyOfficers']) if not mgmt.empty: st.dataframe(mgmt[['name', 'title', 'age']]) else: st.write("No data available") else: st.write("No management data found")

--- ORDERS TAB ---

st.subheader("Latest Orders") st.write("[Sample Placeholder] Displaying latest major orders (Requires custom integration)")

--- NEWS ---

st.subheader("Company & Sector News") st.write("[Sample Placeholder] Displaying recent news headlines")

--- PRODUCT INCOME ---

st.subheader("Revenue by Product/Segment") st.write("[Sample Placeholder] Revenue breakdown by product (requires custom dataset)")

--- FOOTER ---

st.markdown("---") st.markdown("Created by [Your Name]. Data via Yahoo Finance.")

