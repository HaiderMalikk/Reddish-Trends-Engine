"""
This file runs sentiment analysis on Reddit data for a given list of subreddits
and a specific stock symbol. It uses the general_reddit_analysis and
specific_stock_analysis functions from the reddit_analysis module to perform
the analysis.

- it first fetches the stock data using the get_stock_data function from the market_analysis module.
- it then merges the Reddit sentiment analysis with the stock data using the merge_stock_data function.

- for the stock data, it fetches the stock price, etc etc from the yfinance module.
"""

import yfinance as yf


def get_stock_data(symbol: str) -> dict:
    """
    Fetches stock data for a given symbol using yfinance and calculates the RSI value.

    Parameters:
        symbol (str): The stock symbol to fetch data for.

    Returns:
        dict A dictionary containing the current price, daily high, daily low, price change, and RSI value.
        If unable to fetch data, returns an error message.
    """
    try:
        # Fetch stock data using yfinance
        period = "1mo"  # Default period for fetching stock data neede for RSI
        data = yf.download(symbol, period=period, progress=False)

        # If the data length is less than 2, we cannot calculate percentage change
        if data.empty or len(data) < 2:
            return {
                "error": f"${symbol}: possibly delisted; no price data found (period={period})"
            }

        # Calculate RSI
        delta = data["Close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        avg_up = up.rolling(14).mean()
        avg_down = down.rolling(14).mean()
        rs = avg_up / avg_down
        rsi = 100 - (100 / (1 + rs))

        # Get the latest RSI value using the recommended approach
        rsi_value = 0 if rsi.empty else float(rsi.iloc[-1])

        # Calculate percentage change if there's enough data
        previous_close = float(data["Close"].iloc[-2])  # Previous day's closing price
        current_close = float(data["Close"].iloc[-1])  # Today's closing price

        # Percentage change calculation based on 2 previous days
        def calculate_percentage_change(current_price, previous_price):
            return ((current_price - previous_price) / previous_price) * 100

        percentage_change = calculate_percentage_change(current_close, previous_close)

        # Return the data in the requested format with proper float conversions using the latest data
        return {
            "price": round(float(data["Close"].iloc[-1]), 2),
            "high": round(float(data["High"].iloc[-1]), 2),
            "low": round(float(data["Low"].iloc[-1]), 2),
            "change": round(float(data["Close"].iloc[-1] - data["Open"].iloc[-1]), 2),
            "percentage_change": round(percentage_change, 2),
            "rsi": round(rsi_value, 2),
        }

    except Exception:
        error_msg = (
            f"${symbol}: possibly delisted; part of or all data missing (period={period})"
        )
        print(error_msg)
        return {"error": error_msg}


def merge_stock_data(reddit_analysis: dict) -> dict:
    """
    Merges Reddit sentiment analysis with stock data using yfinance.

    Parameters:
        reddit_analysis (dict): A dictionary containing the sentiment analysis results.

    Returns:
        dict: Structured data containing the sentiment analysis results merged with the stock data, structured as follows:
    """
    enriched_data = {}

    for category, stocks in reddit_analysis.items():
        # if no data on specific stock was found skip it
        if stocks is None:
            continue

        enriched_data[category] = []

        for stock, details in stocks:
            stock_symbol = stock.replace("$", "")  # Remove $ sign from symbol
            stock_data = get_stock_data(stock_symbol)

            if "error" in stock_data:
                # Handle the case where no data is found or stock is delisted
                enriched_data[category].append(
                    {
                        "symbol": stock,
                        "count": details["count"],
                        "sentiment": details["sentiment"],
                        "post": details["post"],
                        "price": None,
                        "high": None,
                        "low": None,
                        "change": None,
                        "percentage_change": None,
                        "rsi": None,
                        "error": stock_data["error"],
                    }
                )
            else:
                # Normal case with successful data retrieval
                enriched_data[category].append(
                    {
                        "symbol": stock,
                        "count": details["count"],
                        "sentiment": details["sentiment"],
                        "post": details["post"],
                        "price": stock_data["price"],
                        "high": stock_data["high"],
                        "low": stock_data["low"],
                        "change": stock_data["change"],
                        "percentage_change": stock_data["percentage_change"],
                        "rsi": stock_data["rsi"],
                    }
                )

    return enriched_data
