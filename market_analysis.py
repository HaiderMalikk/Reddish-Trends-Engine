"""
This file runs sentiment analysis on Reddit data for a given list of subreddits
and a specific stock symbol. It uses the general_reddit_analysis and
specific_stock_analysis functions from the reddit_analysis module to perform
the analysis.

- it first fetches the stock data using the get_stock_data function from the market_analysis module.
- it then merges the Reddit sentiment analysis with the stock data using the merge_stock_data function.
- it finally displays the stock analysis in a structured format using the display_stock_analysis function.

- for the stock data, it fetches the stock price, etc etc from Finnhub API. and the RSI, moving averages from yfinance.
- it then calculates the RSI and returns the structured data using pandas DataFrame.
"""

import finnhub
import os
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# Load API keys
load_dotenv()
finnhub_api_key = os.getenv("FINNHUB_API_KEY")

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=finnhub_api_key)


def get_stock_data(symbol):
    """
    Fetches stock data for the given symbol using Finnhub API and calculates the RSI using yfinance.

    Parameters:
        symbol (str): The stock symbol to fetch data for.

    Returns:
        dict: Structured data containing the current price, daily high, daily low, price change, and RSI value.
    """
    try:
        # Get stock quote (price data)
        quote = finnhub_client.quote(symbol)

        # rsi
        # Download data
        data = yf.download(symbol, period="1y", progress=False)

        # Calculate price changes
        delta = data["Close"].diff()

        # Gains and losses
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)

        # Averages in period of 14 days
        avg_up = up.rolling(14).mean()
        avg_down = down.rolling(14).mean()

        # RSI calculation
        rs = avg_up / avg_down
        rsi = 100 - (100 / (1 + rs))

        rsi_value = float(rsi.iloc[-1])

        # Return structured data
        return {
            "price": quote["c"],  # Current price
            "high": quote["h"],  # Daily high
            "low": quote["l"],  # Daily low
            "change": quote["d"],  # Price change
            "rsi": rsi_value,
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def merge_stock_data(reddit_analysis):
    """
    Merges Reddit sentiment analysis with stock data from Finnhub API and calculates the RSI using yfinance.

    Parameters:
        reddit_analysis (dict): A dictionary containing the sentiment analysis results, structured as follows:
            {
                "top_stocks": [...],
                "worst_stocks": [...],
                "rising_stocks": [...]
            }

    Returns:
        dict: Structured data containing the sentiment analysis results merged with the stock data, structured as follows:
            {
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
                        "rsi": stock_data["rsi"],
                    }
                )

    return enriched_data


def display_stock_analysis(merged_data):
    """
    Returns the merged stock analysis data in a structured format.

    Parameters:
        merged_data (dict): Structured data containing the sentiment analysis results merged with the stock data, structured as follows:
            {
                "top_stocks": [...],
                "worst_stocks": [...],
                "rising_stocks": [...]
            }

    Returns:
        dict: A dictionary containing DataFrames for each category.
    """
    dataframes = {}
    for category, stocks in merged_data.items():
        df = pd.DataFrame(stocks)
        dataframes[category] = df
    return dataframes
