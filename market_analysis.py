"""
This module provides functions for analyzing stock market data using yfinance and calculating various metrics such as
percentage change and Relative Strength Index (RSI). It includes functions to perform daily, short period, monthly,
and long period analyses of stock data. Additionally, it fetches stock data for a given symbol and period, and merges
Reddit sentiment analysis with the stock data.
Functions:
- calculate_percentage_change(current_price, previous_price): Calculates the percentage change between two prices.
- calculate_rsi(data, periods=14): Calculates the Relative Strength Index (RSI) based on closing prices.
- daily_analysis(data, company_name): Analyzes stock data for a daily period.
- short_period_analysis(data, company_name): Analyzes stock data for short periods (5 days).
- monthly_analysis(data, company_name): Analyzes stock data for a monthly period.
- long_period_analysis(data, company_name): Analyzes stock data for long periods (3 months, 6 months, 1 year, etc.).
- get_stock_data(symbol, stock_period): Fetches stock data for a given symbol and period using yfinance and calculates the RSI value.
- merge_stock_data(reddit_analysis, stock_period): Merges Reddit sentiment analysis with stock data using yfinance.
"""

import yfinance as yf


def calculate_percentage_change(current_price, previous_price):
    """
    Calculate percentage change between two prices.

    Parameters:
        current_price (float): Current price
        previous_price (float): Previous price

    Returns:
        float: Percentage change
    """
    return ((current_price - previous_price) / previous_price) * 100


def calculate_rsi(data, periods=14):
    """
    Calculate RSI based on closing prices.

    Parameters:
        data (DataFrame): Stock price data
        periods (int): Number of periods for RSI calculation

    Returns:
        float: The RSI value or 0 if not enough data
    """
    if len(data) < periods + 1:
        return 0

    delta = data["Close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_up = up.rolling(periods).mean()
    avg_down = down.rolling(periods).mean()
    rs = avg_up / avg_down
    rsi = 100 - (100 / (1 + rs))

    return 0 if rsi.empty else float(rsi.iloc[-1])


def daily_analysis(data, company_name):
    """
    Analyze stock data for daily period.

    Parameters:
        data (DataFrame): Stock price data
        company_name (str): Company name

    Returns:
        dict: Stock analysis data for daily period
    """
    current_close = float(data["Close"].iloc[-1])

    # For daily, we compare close with open
    percentage_change = calculate_percentage_change(
        current_close, float(data["Open"].iloc[-1])
    )

    # Calculate RSI even for daily period
    rsi_value = calculate_rsi(data)

    return {
        "company_name": company_name,
        "price": round(current_close, 2),
        "high": round(float(data["High"].iloc[-1]), 2),
        "low": round(float(data["Low"].iloc[-1]), 2),
        "change": round(float(data["Close"].iloc[-1] - data["Open"].iloc[-1]), 2),
        "percentage_change": round(percentage_change, 2),
        "rsi": round(rsi_value, 2),
    }


def short_period_analysis(data, company_name):
    """
    Analyze stock data for short periods (5d).

    Parameters:
        data (DataFrame): Stock price data
        company_name (str): Company name

    Returns:
        dict: Stock analysis data for short period
    """
    current_close = float(data["Close"].iloc[-1])
    first_open = float(data["Open"].iloc[0])

    # Find high and low for the entire period
    period_high = float(data["High"].max())
    period_low = float(data["Low"].min())

    percentage_change = calculate_percentage_change(current_close, first_open)

    # Calculate RSI for short period too, it will return 0 if not enough data
    rsi_value = calculate_rsi(data)

    return {
        "company_name": company_name,
        "price": round(current_close, 2),
        "high": round(period_high, 2),
        "low": round(period_low, 2),
        "change": round(current_close - first_open, 2),
        "percentage_change": round(percentage_change, 2),
        "rsi": round(rsi_value, 2),
    }


def monthly_analysis(data, company_name):
    """
    Analyze stock data for monthly period.

    Parameters:
        data (DataFrame): Stock price data
        company_name (str): Company name

    Returns:
        dict: Stock analysis data for monthly period
    """
    current_close = float(data["Close"].iloc[-1])
    first_open = float(data["Open"].iloc[0])

    # Find high and low for the entire period
    period_high = float(data["High"].max())
    period_low = float(data["Low"].min())

    percentage_change = calculate_percentage_change(current_close, first_open)

    # Calculate RSI for monthly and longer periods
    rsi_value = calculate_rsi(data)

    return {
        "company_name": company_name,
        "price": round(current_close, 2),
        "high": round(period_high, 2),
        "low": round(period_low, 2),
        "change": round(current_close - first_open, 2),
        "percentage_change": round(percentage_change, 2),
        "rsi": round(rsi_value, 2),
    }


def long_period_analysis(data, company_name):
    """
    Analyze stock data for long periods (3mo, 6mo, 1y, etc.)

    Parameters:
        data (DataFrame): Stock price data
        company_name (str): Company name

    Returns:
        dict: Stock analysis data for long period
    """
    current_close = float(data["Close"].iloc[-1])
    first_open = float(data["Open"].iloc[0])

    # Find high and low for the entire period
    period_high = float(data["High"].max())
    period_low = float(data["Low"].min())

    percentage_change = calculate_percentage_change(current_close, first_open)

    # Calculate RSI for monthly and longer periods
    rsi_value = calculate_rsi(data)

    return {
        "company_name": company_name,
        "price": round(current_close, 2),
        "high": round(period_high, 2),
        "low": round(period_low, 2),
        "change": round(current_close - first_open, 2),
        "percentage_change": round(percentage_change, 2),
        "rsi": round(rsi_value, 2),
    }


def get_stock_data(symbol: str, stock_period: str) -> dict:
    """
    Fetches stock data for a given symbol using yfinance and calculates the RSI value.

    Parameters:
        symbol (str): The stock symbol to fetch data for.
        stock_period (str): The period for fetching stock data. available options are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    Returns:
        dict A dictionary containing the current price, daily high, daily low, price change, and RSI value.
        If unable to fetch data, returns an error message.
    """
    try:
        # Fetch stock data using yfinance
        data = yf.download(symbol, period=stock_period, progress=False)

        # If the data length is less than 2, we cannot calculate percentage change
        if data.empty or len(data) < 2:
            return {
                "error": f"${symbol}: possibly delisted; no price data found (period={stock_period})"
            }

        # get company name from the symbol
        company = yf.Ticker(symbol)
        company_name = company.info["longName"]

        # Call the appropriate analysis function based on the period
        if stock_period == "1d":
            return daily_analysis(data, company_name)
        elif stock_period == "5d":
            return short_period_analysis(data, company_name)
        elif stock_period == "1mo":
            return monthly_analysis(data, company_name)
        else:  # 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            return long_period_analysis(data, company_name)

    except Exception as e:
        error_msg = f"${symbol}: possibly delisted; part of or all data missing (period={stock_period}). Error: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


def merge_stock_data(reddit_analysis: dict, stock_period: str) -> dict:
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
            stock_data = get_stock_data(stock_symbol, stock_period)

            if "error" in stock_data:
                # Handle the case where no data is found or stock is delisted
                enriched_data[category].append(
                    {
                        "symbol": stock,
                        "company_name": None,
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
                        "company_name": stock_data["company_name"],
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
