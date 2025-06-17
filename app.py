# --- STREAMLIT DASHBOARD UPGRADE: COMBINED FEATURES ---

import streamlit as st
import yfinance as yf
import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta
from textblob import TextBlob  # For sentiment analysis

# 🛠️ Must be the FIRST Streamlit command
st.set_page_config(page_title="📊 Investorly - Stock Dashboard", layout="wide")

FAV_FILE = "favorites.json"
SETTINGS_FILE = "settings.json"

# --- Utility Functions ---
@st.cache_data(ttl=300)
def cached_load_data(ticker, interval="1d", period="1mo"):
    df = yf.download(ticker, interval=interval, period=period, progress=False)
    df.reset_index(inplace=True)
    return df

def load_favorites():
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    return []

def save_favorites(favs):
    with open(FAV_FILE, "w") as f:
        json.dump(list(set(favs)), f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"discord_url": ""}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# --- Routing between Dashboard and Settings ---
mode = st.sidebar.radio("🔧 Navigation", ["Dashboard", "Settings"])
settings = load_settings()

if mode == "Settings":
    st.title("⚙️ Settings")
    discord_url = st.text_input("Discord Webhook URL", value=settings.get("discord_url", ""))
    if st.button("📂 Save Settings"):
        settings = {"discord_url": discord_url}
        save_settings(settings)
        st.success("Settings saved.")
    if st.button("📢 Send Test Notification") and discord_url:
        try:
            response = requests.post(discord_url, json={"content": "✅ This is a test notification from your stock dashboard."})
            if response.status_code == 204:
                st.success("Test message sent!")
            else:
                st.error(f"Failed to send: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")
    st.stop()

# ALERT CHECK for each favorite
favorites = load_favorites()
for fav in favorites:
    hist = yf.Ticker(fav).history(period="2d")
    if len(hist) >= 2:
        prev_close = hist["Close"].iloc[-2]
        last_close = hist["Close"].iloc[-1]
        pct_change = ((last_close - prev_close) / prev_close) * 100
        if abs(pct_change) >= 5 and settings.get("discord_url"):
            try:
                msg = f"⚠️ {fav} moved {pct_change:.2f}% in the last day."
                requests.post(settings["discord_url"], json={"content": msg})
            except:
                pass

# Sidebar Stock Selection
st.sidebar.header("🔍 Choose or Add a Stock")
def_ticker = favorites[0] if favorites else "AAPL"
custom_ticker = st.sidebar.text_input("Enter stock ticker:", value=def_ticker).upper()
selected_tickers = st.sidebar.multiselect("Top Stocks", sorted([
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "TSLA", "UNH", "JNJ", "V", "PG", "JPM",
    "XOM", "HD", "MA", "LLY", "MRK", "PEP", "KO", "CVX"
]), default=[def_ticker])
selected_ticker = selected_tickers[0] if selected_tickers else def_ticker
ticker = custom_ticker if custom_ticker else selected_ticker

if st.sidebar.button("⭐ Add to Favorites"):
    favorites.append(ticker)
    save_favorites(favorites)
if st.sidebar.button("❌ Remove from Favorites"):
    favorites = [t for t in favorites if t != ticker]
    save_favorites(favorites)
if favorites:
    st.sidebar.markdown("### ⭐ Favorites")
    for fav in favorites:
        if st.sidebar.button(f"🔄 Load {fav}"):
            ticker = fav

# Load data
st.subheader(f"📈 {ticker} — 1 Day (5-min interval)")
intraday_data = cached_load_data(ticker, interval="5m", period="1d")
if not intraday_data.empty:
    st.line_chart(intraday_data.set_index("Datetime")["Close"])

st.subheader(f"📅 {ticker} — Past 1 Month (Daily)")
daily_data = cached_load_data(ticker)
st.line_chart(daily_data.set_index("Date")["Close"])

# Volume Chart
st.subheader("📊 Volume (1 Month)")
st.bar_chart(daily_data.set_index("Date")["Volume"])

# Performance Summary
st.markdown("---")
st.subheader("📊 Performance Summary")
ticker_obj = yf.Ticker(ticker)

# --- SAFELY FETCH INFO ---
info = {}
try:
    raw_info = ticker_obj.info
    if raw_info and isinstance(raw_info, dict):
        info = raw_info
    else:
        raise ValueError("No valid info returned from yfinance.")
except Exception as e:
    st.warning(f"⚠️ Failed to fetch stock info: {e}")

hist = ticker_obj.history(period="6mo")
hist = hist[hist["Close"].notna()]

try:
    latest_date = hist.index[-1]
    latest_close = hist["Close"].iloc[-1]

    def get_close_on_or_before(days_ago):
        target_date = latest_date - timedelta(days=days_ago)
        filtered = hist[hist.index <= target_date]
        return filtered["Close"].iloc[-1] if not filtered.empty else None

    close_1d = get_close_on_or_before(1)
    close_7d = get_close_on_or_before(7)
    close_30d = get_close_on_or_before(30)

    pct_1d = f"{((latest_close - close_1d) / close_1d * 100):.2f}%" if close_1d else "N/A"
    pct_1w = f"{((latest_close - close_7d) / close_7d * 100):.2f}%" if close_7d else "N/A"
    pct_1m = f"{((latest_close - close_30d) / close_30d * 100):.2f}%" if close_30d else "N/A"

    row1 = st.columns(3)
    row1[0].metric("1D Change", pct_1d)
    row1[1].metric("1W Change", pct_1w)
    row1[2].metric("1M Change", pct_1m)

    row2 = st.columns(2)
    row2[0].metric("52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
    row2[1].metric("52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}")
except Exception as e:
    st.warning(f"⚠️ Unable to calculate performance metrics: {e}")

# Earnings & Dividend Info
st.subheader("💰 Earnings & Dividend Info")
earn_date = info.get("earningsDate", None)
div_yield = info.get("dividendYield", None)

earn_str = "N/A"
if earn_date:
    try:
        if isinstance(earn_date, list):
            earn_date = earn_date[0]
        earn_str = pd.to_datetime(earn_date).strftime("%b %d, %Y")
    except Exception:
        pass

col1, col2 = st.columns(2)
col1.markdown(f"**Next Earnings Date:** {earn_str}")
col2.markdown(f"**Dividend Yield:** {round(div_yield * 100, 2)}%" if div_yield else "No Dividend")

# Analyst Ratings
st.subheader("📋 Analyst Ratings")
target_price = info.get("targetMeanPrice", None)
recommendation = info.get("recommendationMean", None)

col1, col2 = st.columns(2)
if target_price:
    col1.markdown(f"**Avg Target Price:** ${target_price}")
if recommendation:
    rating_scale = {
        1.0: "Strong Buy",
        2.0: "Buy",
        3.0: "Hold",
        4.0: "Underperform",
        5.0: "Sell",
    }
    label = rating_scale.get(round(float(recommendation)), "N/A")
    col2.markdown(f"**Analyst Consensus:** {label} ({recommendation}/5)")
else:
    col2.markdown("No analyst rating available.")

# External Finance Link (Google News)
st.subheader(f"📰 News & More for {ticker}")
google_finance_url = f"https://www.google.com/finance/quote/{ticker}:NASDAQ"
st.markdown(f"[🔗 View news on Google Finance]({google_finance_url})")
