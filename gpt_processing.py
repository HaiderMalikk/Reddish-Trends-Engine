""" 
This module provides functionality to analyze stock data using OpenAI's GPT model.

The module authenticates with the OpenAI API and defines a function to analyze stock data sourced from a subreddit.
The analysis includes an overview, market sentiment, technical analysis, fundamental analysis, and prediction of future stock performance.

Functions:
- analyze_stock_data_with_gpt(stock_data): Analyzes stock data using a GPT model and returns the analysis in JSON format.

Dependencies:
-------------
- openai: For interacting with the OpenAI API.
- os: For accessing environment variables.
- json: For handling JSON data.
- dotenv: For loading environment variables from a .env file.
"""

import openai
import os
import json
from dotenv import load_dotenv  # For loading environment variables

load_dotenv()
print("🛑 Authenticating Open AI")
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)
print("✅ Open AI Auth Complete\n")


def analyze_stock_data_with_gpt(stock_data):
    """
    Analyze stock data sourced from a subreddit with a Large Language Model (LLM).

    Parameters
    ----------
    stock_data : dict
        A dictionary containing the stock symbol, count, sentiment, post, price, high, low, change, percentage change, and RSI.
        The dictionary may contain data for one of the following categories: best, worst, and rising stocks.

    Returns
    -------
    dict
        A dictionary containing the analysis of the stock data. The analysis includes an overview, market sentiment, technical analysis, fundamental analysis, and prediction.
    """
    print("🤖 Analyzing Stock Data with GPT")
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheap model because 🚫💰
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert financial analyst with deep knowledge of stock and crypto markets. "
                    "You analyze trends, fundamental & technical indicators, and market sentiment. "
                    "You will receive a dictionary of stock data sourced from a subreddit, which may be for best, worst, or rising stocks. "
                    "The dictionary contains the stock symbol, company name, count, sentiment, post, price, high, low, change, percentage change, and RSI. "
                    "The price, high, low, change, and percentage change are all for the day the RSI is over 30 days"
                    "Your task is to analyze the data and predict future stock performance with detailed reasoning."
                    "Base your predictions on technical indicators, fundamentals, market trends, and news sentiment. "
                    "Provide insights **strictly in JSON format** with the following structure:\n\n"
                    "{\n"
                    '  "overview": "Brief summary of stock performance.",\n'
                    '  "market_sentiment": "Analysis of public sentiment.",\n'
                    '  "technical_analysis": "Stock trend insights.",\n'
                    '  "fundamental_analysis": "Financial health insights.",\n'
                    '  "prediction": "Future performance prediction."\n'
                    '  "Confidence Score": "Confidence level of prediction as a number between 0 and 100."\n'
                    "}"
                ),
            },
            {
                "role": "user",
                "content": f"Here is the stock data in JSON format: {json.dumps(stock_data)}. Please analyze it and return a response in JSON format. NOTE: you have only 300 tokens to respond make sure you fit in the limit go under if you need to.",
            },
        ],
        temperature=0.3,  # low temp for factual response
        max_tokens=300,  # 300 words max
        frequency_penalty=0.2,  # less repetition
        presence_penalty=0.3,  # less repetition
        response_format={"type": "json_object"},  # return JSON format
    )

    print("✅ GPT Analysis Complete")
    return json.loads(response.choices[0].message.content)
