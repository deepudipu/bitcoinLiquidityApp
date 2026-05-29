import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Bitcoin Liquidity Dashboard",
    layout="wide"
)

st.title("Bitcoin Liquidity Dashboard")

# Sidebar Range Selector
range_percent = st.sidebar.selectbox(
    "Select Liquidity Range (%)",
    [3, 5, 10],
    index=1
)

try:
    # Get Current BTC Price
    ticker_url = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
    ticker_response = requests.get(ticker_url, timeout=10)
    ticker_data = ticker_response.json()

    current_price = float(ticker_data["price"])

    # Get Order Book
    book_url = "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2"
    book_response = requests.get(book_url, timeout=10)
    book_data = book_response.json()

    bids = book_data["bids"]
    asks = book_data["asks"]

    # Calculate Range
    lower_price = current_price * (1 - range_percent / 100)
    upper_price = current_price * (1 + range_percent / 100)

    buy_orders = []
    sell_orders = []

    total_buy_liquidity = 0
    total_sell_liquidity = 0

    # BUY SIDE (Below Current Price)
    for row in bids:
        price = float(row[0])
        qty = float(row[1])

        if lower_price <= price <= current_price:
            liquidity = price * qty

            total_buy_liquidity += liquidity

            buy_orders.append({
                "Price": price,
                "BTC Qty": qty,
                "Liquidity USD": liquidity
            })

    # SELL SIDE (Above Current Price)
    for row in asks:
        price = float(row[0])
        qty = float(row[1])

        if current_price <= price <= upper_price:
            liquidity = price * qty

            total_sell_liquidity += liquidity

            sell_orders.append({
                "Price": price,
                "BTC Qty": qty,
                "Liquidity USD": liquidity
            })

    # Top 5 Liquidity Levels
    top_bids = sorted(
        buy_orders,
        key=lambda x: x["Liquidity USD"],
        reverse=True
    )[:5]

    top_asks = sorted(
        sell_orders,
        key=lambda x: x["Liquidity USD"],
        reverse=True
    )[:5]

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current BTC Price",
            f"${current_price:,.2f}"
        )

    with col2:
        st.metric(
            f"Buy Liquidity ({range_percent}%)",
            f"${total_buy_liquidity:,.0f}"
        )

    with col3:
        st.metric(
            f"Sell Liquidity ({range_percent}%)",
            f"${total_sell_liquidity:,.0f}"
        )

    st.info(
        f"Analyzing liquidity from ${lower_price:,.0f} to ${upper_price:,.0f}"
    )

    st.caption(
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Buy Table
    st.subheader(
        f"Top 5 Buy Liquidity Levels Within {range_percent}%"
    )

    bid_df = pd.DataFrame(top_bids)

    if not bid_df.empty:
        display_bid_df = bid_df.copy()

        display_bid_df["Price"] = display_bid_df["Price"].map(
            lambda x: f"${x:,.2f}"
        )

        display_bid_df["Liquidity USD"] = display_bid_df["Liquidity USD"].map(
            lambda x: f"${x:,.2f}"
        )

        st.table(display_bid_df)
    else:
        st.warning("No buy liquidity found in selected range.")

    # Sell Table
    st.subheader(
        f"Top 5 Sell Liquidity Levels Within {range_percent}%"
    )

    ask_df = pd.DataFrame(top_asks)

    if not ask_df.empty:
        display_ask_df = ask_df.copy()

        display_ask_df["Price"] = display_ask_df["Price"].map(
            lambda x: f"${x:,.2f}"
        )

        display_ask_df["Liquidity USD"] = display_ask_df["Liquidity USD"].map(
            lambda x: f"${x:,.2f}"
        )

        st.table(display_ask_df)
    else:
        st.warning("No sell liquidity found in selected range.")

    # Liquidity Comparison Chart
    st.subheader("Buy vs Sell Liquidity")

    chart_df = pd.DataFrame({
        "Liquidity Type": ["Buy", "Sell"],
        "USD Value": [
            total_buy_liquidity,
            total_sell_liquidity
        ]
    })

    st.bar_chart(
        chart_df.set_index("Liquidity Type")
    )

except Exception as e:
    st.error(f"Application Error: {e}")