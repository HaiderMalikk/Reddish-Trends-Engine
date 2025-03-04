"""
Reddit Data Analysis Script

This script performs sentiment analysis on Reddit posts and comments to analyze stock mentions and their sentiments.
It uses the PRAW (Python Reddit API Wrapper) to fetch data from Reddit and the VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis tool to analyze the sentiment of the text.

Steps to get to the final output:

1. **API Client Initialization**:
    - Initialize the OpenAI client using the OpenAI API key.
    - Authenticate with the Reddit API using the credentials and create a Reddit client.

2. **Fetch Reddit Posts**:
    - Define a function `get_reddit_posts` to fetch posts and comments from a specified subreddit.
    - The function retrieves the titles, selftexts, and comments of the fetched posts.

3. **Sentiment Analysis**:
    - Initialize the VADER sentiment analyzer.
    - Define a function `analyze_sentiment` to analyze the sentiment of a given text.
    - The function returns a sentiment score ranging from -1 (negative) to +1 (positive).

4. **Normalize Sentiment Scores**:
    - Define a function `normalize_score` to boost sentiment scores to improve ranking impact.
    - The function amplifies positive and negative scores.

5. **Extract Stock Mentions**:
    - Define a function `extract_stock_mentions` to extract stock tickers (e.g., $TSLA, $AAPL) from the posts and track their sentiment.
    - The function uses regular expressions to find stock tickers and calculates the average sentiment for each stock.

6. **Classify Stocks**:
    - Define a function `classify_stocks` to classify stocks mentioned in a subreddit's posts based on sentiment analysis.
    - The function returns a dictionary containing lists of stocks classified into three categories:
        - "top_stocks": The top 5 stocks with the highest sentiment scores.
        - "worst_stocks": The bottom 5 stocks with the lowest sentiment scores.
        - "rising_stocks": Stocks with sentiment scores above 0.5, indicating positive sentiment.

7. **Specific Stock Analysis**:
    - Define a function `specific_stock_analysis` to return sentiment and mentions for a specific stock.
    - The function retrieves posts from a subreddit, extracts stock mentions, and returns a formatted string containing the stock's sentiment and mention counts.

8. **General Reddit Analysis**:
    - Define a function `general_reddit_analysis` to perform general stock analysis for a subreddit.
    - The function analyzes the subreddit and returns the results.

Usage:
    - Run the script to authenticate with Reddit and OpenAI, fetch Reddit posts, perform sentiment analysis, and classify stocks based on sentiment.
    - The script prints out the general stock analysis for the specified subreddit and the specific stock analysis for the specified stock.

Example:
    - To analyze the sentiment of stocks mentioned in the "wallstreetbets" subreddit and get the analysis for the stock "TSLA":
        ```
        subreddit = "wallstreetbets"
        stock = "TSLA"
        limit = 20
        general_analysis = general_reddit_analysis(subreddit, limit)
        specific_analysis = specific_stock_analysis(subreddit, stock, limit)
        print(general_analysis)
        print(specific_analysis)
        ```
NOTE: only one subbreddit can be analyzed at a time, while you can input a whole array of subreddits
in the main function each subreddit will be analyzed one at a time on multiple threads.
this is more efficient than analyzing all subreddits at once, its possible beacuse each subreddit is independent of the other.
"""

import praw  # Python Reddit API Wrapper
import os  # Operating System for environment variables
from dotenv import load_dotenv  # For loading environment variables
from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer,
)  # Sentiment analysis
from collections import defaultdict  # For tracking stock mentions
import re  # For getting stock name from post and coverting to ticker

print("🛑 Authenticating")

load_dotenv()

# Reddit API credentials from .env file
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")

# Reddit API authentication
reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent=reddit_user_agent,
    username=reddit_username,
    password=reddit_password,
)

# Print success message
print(f"✅ Authenticated as: {reddit.user.me()}\n")


def get_reddit_posts(subreddit: str, limit: int) -> list:
    """
    Fetch posts and comments from a specified subreddit.

    Parameters:
        subreddit (str): The name of the subreddit to fetch posts from.
        limit (int): The maximum number of posts to retrieve.

    Returns:
        list: A list containing the titles, selftexts, and comments of the fetched posts.
    """
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        posts.append(f"{submission.title} {submission.selftext}")
        submission.comments.replace_more(limit=0)  # Load top-level comments only
        posts.extend(comment.body for comment in submission.comments)
    return posts


# Sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of a given text.

    Parameters:
        text (str): The text to analyze sentiment of.

    Returns:
        float: The sentiment score of the text, ranging from -1 (negative) to +1 (positive).
    """
    return analyzer.polarity_scores(text)[
        "compound"
    ]  # Ranges from -1 (negative) to +1 (positive)


def normalize_score(score: float) -> float:
    """
    Boosts sentiment scores to improve ranking impact.

    Parameters:
        score (float): The sentiment score to normalize.

    Returns:
        float: The normalized sentiment score.
    """
    return score * 10 if score > 0 or score < 0 else 0


def extract_stock_mentions(posts: list) -> dict:
    """
    Extracts stock tickers like $TSLA, $AAPL and tracks their sentiment

    Parameters:
        posts (list): A list of strings containing the text of the posts to analyze.

    Returns:
        dict: A dictionary containing the stock symbols and their associated sentiment scores.
    """
    # Track stock mentions using a dictionary with a count a and list of sentiment scores, def inside function to reset each time
    stock_mentions = defaultdict(
        lambda: {"count": 0, "sentiment": []}
    )  # Track stock mentions
    stock_pattern = r"\$[A-Z]+"
    for post in posts:
        matches = re.findall(stock_pattern, post)
        sentiment = analyze_sentiment(post)
        for stock in matches:
            stock_mentions[stock]["count"] += 1
            stock_mentions[stock]["sentiment"].append(sentiment)

    # Calculate average sentiment per stock
    for stock in stock_mentions:
        avg_sentiment = sum(stock_mentions[stock]["sentiment"]) / len(
            stock_mentions[stock]["sentiment"]
        )
        stock_mentions[stock]["sentiment"] = normalize_score(avg_sentiment)

    return stock_mentions


def classify_stocks(subreddit: str, limit: int) -> dict:
    """
    Classifies stocks mentioned in a subreddit's posts based on sentiment analysis.

    Parameters:
        subreddit (str): The name of the subreddit to analyze.
        limit (int): The maximum number of posts to retrieve.

    Returns:
        dict: A dictionary containing lists of stocks classified into three categories:
            - "top_stocks": The top 5 stocks with the highest sentiment scores.
            - "worst_stocks": The bottom 5 stocks with the lowest sentiment scores.
            - "rising_stocks": Stocks with sentiment scores above 0.5, indicating positive sentiment.
    """
    posts = get_reddit_posts(subreddit, limit)
    sentiment_data = extract_stock_mentions(posts)

    # Sort stocks by sentiment
    sorted_stocks = sorted(
        sentiment_data.items(), key=lambda x: x[1]["sentiment"], reverse=True
    )

    # Split into top, worst, and rising stocks, split the limit in half as thats the number of posts we have i.e potential stocks we have
    # since the stocks are sorted by sentiment we can just split the list in half and take the top and bottom as the top and worst stocks
    top_stocks = sorted_stocks[: limit // 2]
    worst_stocks = sorted_stocks[-limit // 2 :]
    rising_stocks = [
        s for s in sorted_stocks if s[1]["sentiment"] > 0.5
    ]  # Positive sentiment threshold

    return {
        "top_stocks": top_stocks,
        "worst_stocks": worst_stocks,
        "rising_stocks": rising_stocks,
    }


def get_stock_analysis(stock: str, subreddit: str, limit: int) -> dict:
    """
    Returns sentiment and mentions for a specific stock.

    Parameters:
        stock (str): The stock symbol to analyze. must be in the format TSLA for Tesla, AAPL for Apple, etc.
        subreddit (str): The name of the subreddit to analyze.
        limit (int): The maximum number of posts to retrieve.

    Returns:
        str: A formatted string containing the stock's sentiment and mention counts.
    """
    posts = get_reddit_posts(subreddit, limit)
    stock_data = extract_stock_mentions(posts)

    if stock not in stock_data:
        return {"specific_stock": [(stock, {"count": 0, "sentiment": 0})]}

    data = stock_data[stock]
    return {
        "specific_stock": [
            (stock, {"count": data["count"], "sentiment": data["sentiment"]})
        ]
    }


# Main functions for general and specific analysis
def general_reddit_analysis(subreddit: str, limit: int) -> dict:
    """
    Perform general stock analysis for a subreddit.

    Parameters:
        subreddit (str): The name of the subreddit to analyze.
        limit (int): The maximum number of posts to retrieve.

    Returns:
        dict: A dictionary containing the general stock analysis for the subreddit.
    """
    return classify_stocks(subreddit, limit)


def specific_stock_analysis(subreddit: str, stock: str, limit: int) -> dict:
    """
    Perform specific stock analysis for a subreddit.

    Parameters:
        subreddit (str): The name of the subreddit to analyze.
        stock (str): The stock symbol to analyze. must be in the format TSLA
        limit (int): The maximum number of posts to retrieve.

    Returns:
        dict: A dictionary containing the specific stock analysis for the subreddit.
    """
    return get_stock_analysis(stock, subreddit, limit)
