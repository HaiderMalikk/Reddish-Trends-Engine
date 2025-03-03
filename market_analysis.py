"""
This file runs sentiment analysis on Reddit data for a given list of subreddits
and a specific stock symbol. It uses the general_reddit_analysis and
specific_stock_analysis functions from the reddit_analysis module to perform
the analysis.

- it first fetches the stock data using the get_stock_data function from the market_analysis module.
- it then merges the Reddit sentiment analysis with the stock data using the merge_stock_data function.
- it finally displays the stock analysis in a structured format using the display_stock_analysis function.

- for the stock data, it fetches the stock price, etc etc from the yfinance module.\
"""

import yfinance as yf


def get_stock_data(symbol: str, period: str = "1mo") -> dict | None:
    """
    Fetches stock data for a given symbol using yfinance and calculates the RSI value.

    Parameters:
        symbol (str): The stock symbol to fetch data for.
        period (str): The period for which to fetch data. Defaults to "1mo".

    Returns:
        dict | None: A dictionary containing the current price, daily high, daily low, price change, and RSI value. If unable to fetch data, returns None.
    """
    try:
        # Fetch stock data using yfinance
        data = yf.download(symbol, period=period, progress=False)

        # If the data length is less than 2, we cannot calculate percentage change
        if data.empty or len(data) < 2:
            return {"error": "Not enough data to calculate percentage change."}

        # Calculate RSI
        delta = data["Close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        avg_up = up.rolling(14).mean()
        avg_down = down.rolling(14).mean()
        rs = avg_up / avg_down
        rsi = 100 - (100 / (1 + rs))

        # Get the latest RSI value using the recommended approach
        rsi_value = None if rsi.empty else float(rsi.iloc[-1])

        if rsi_value is None:
            return {"error": "Unable to calculate RSI. Data may be insufficient."}

        # Calculate percentage change if there's enough data
        previous_close = float(data["Close"].iloc[-2])  # Previous day's closing price
        current_close = float(data["Close"].iloc[-1])  # Today's closing price

        # Percentage change calculation
        def calculate_percentage_change(current_price, previous_price):
            return ((current_price - previous_price) / previous_price) * 100

        percentage_change = calculate_percentage_change(current_close, previous_close)

        # Return the data in the requested format with proper float conversions
        return {
            "price": round(float(data["Close"].iloc[-1]), 2),
            "high": round(float(data["High"].iloc[-1]), 2),
            "low": round(float(data["Low"].iloc[-1]), 2),
            "change": round(float(data["Close"].iloc[-1] - data["Open"].iloc[-1]), 2),
            "percentage_change": round(percentage_change, 2),
            "rsi": round(rsi_value, 2),
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def merge_stock_data(reddit_analysis: dict) -> dict:
    """
    Merges Reddit sentiment analysis with stock data using yfinance.

    Parameters:
        reddit_analysis (dict): A dictionary containing the sentiment analysis results, structured as follows:
            subreddit: {
                "top_stocks": [...],
                "worst_stocks": [...],
                "rising_stocks": [...]
            }

    Returns:
        dict: Structured data containing the sentiment analysis results merged with the stock data, structured as follows:
            subreddit: {
                "top_stocks": [...],
                "worst_stocks": [...],
                "rising_stocks": [...]
            }
    """
    enriched_data = {}

    for category, stocks in reddit_analysis.items():
        enriched_data[category] = []

        for stock, details in stocks:
            stock_symbol = stock.replace("$", "")  # Remove $ sign from symbol
            if stock_data := get_stock_data(stock_symbol):
                enriched_data[category].append(
                    {
                        "symbol": stock,
                        "count": details["count"],
                        "sentiment": details["sentiment"],
                        "price": stock_data["price"],
                        "high": stock_data["high"],
                        "low": stock_data["low"],
                        "change": stock_data["change"],
                        "percentage_change": stock_data["percentage_change"],
                        "rsi": stock_data["rsi"],
                    }
                )

    return enriched_data
