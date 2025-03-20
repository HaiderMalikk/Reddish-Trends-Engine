"""
This module performs sentiment analysis on Reddit posts to identify and analyze stock mentions.

Modules:
- praw: Python Reddit API Wrapper for accessing Reddit data.
- os: Operating System module for accessing environment variables.
- dotenv: For loading environment variables from a .env file.
- vaderSentiment: Sentiment analysis tool for analyzing text sentiment.
- collections: For creating a default dictionary to track stock mentions.
- re: Regular expressions for extracting stock symbols from text.

Functions:
- get_reddit_posts: Fetches posts and comments from a specified subreddit.
- analyze_sentiment: Analyzes the sentiment of a given text.
- normalize_score: Normalizes sentiment scores to improve ranking impact.
- parse_post_text: Parses a post text string into a structured dictionary.
- extract_stock_mentions: Extracts stock tickers and tracks their sentiment.
- get_reddit_analysis: Classifies stocks mentioned in a subreddit's posts based on sentiment analysis.
- get_stock_analysis: Returns sentiment and mentions for specific stocks.
- general_reddit_analysis: Performs general stock analysis for a subreddit.
- specific_stock_analysis: Performs specific stock analysis for a subreddit.
"""

import praw  # Python Reddit API Wrapper
import os  # Operating System for environment variables
from dotenv import load_dotenv  # For loading environment variables
from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer,
)  # Sentiment analysis
from collections import defaultdict  # For tracking stock mentions
import re  # For getting stock name from post and coverting to ticker

print("🛑 Authenticating Reddit API")

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


def get_reddit_posts(
    subreddit: str,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
) -> list:
    """
    Fetch posts and comments from a specified subreddit.

    Parameters:
        subreddit (str): The name of the subreddit to fetch posts from.
        limit (int): The maximum number of posts to retrieve.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", rising and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.

    Returns:
        list: A list of dictionaries containing the post title, text, comments, and link.
    """

    posts = []
    # Get the subreddit method (hot, new, top, etc.)
    subreddit_method = reddit.subreddit(subreddit).__getattr__(post_type)

    # Call the method with appropriate parameters based on whether time_filter is provided
    if time_filter is not None and post_type in {"top", "controversial"}:
        submissions = subreddit_method(time_filter=time_filter, limit=limit)
    else:
        submissions = subreddit_method(limit=limit)

    for submission in submissions:
        post = {
            "title": submission.title,
            "text": submission.selftext,
            "comments": [],
            "link": submission.url,
        }

        submission.comments.replace_more(limit=0)  # Load top-level comments only

        postnum = 1
        for comment in submission.comments:
            if comment.body:
                post["comments"].append(f"Comment {postnum}: {comment.body}")
                postnum += 1
                if postnum > comment_limit:
                    break

        # For sentiment analysis, combine all text
        post["full_text"] = (
            f"Post Title: {post['title']} Post Text: {post['text']} Post Link: {post['link']} Top Comments:"
            + " ".join(post["comments"])
        )
        posts.append(post)

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
        dict: A dictionary containing the stock symbols and their associated sentiment scores along with the actual post used for analysis.
    """

    stock_mentions = defaultdict(lambda: {"count": 0, "sentiment": []})
    stock_pattern = r"\$[A-Z]+"

    for post in posts:
        text = post["full_text"]

        matches = re.findall(stock_pattern, text)
        sentiment = analyze_sentiment(text)

        for stock in matches:
            stock_mentions[stock]["count"] += 1
            stock_mentions[stock]["sentiment"].append(round(sentiment, 2))
            stock_mentions[stock]["post"] = post

    # Calculate average sentiment per stock
    for stock in stock_mentions:
        if stock_mentions[stock]["sentiment"]:
            avg_sentiment = sum(stock_mentions[stock]["sentiment"]) / len(
                stock_mentions[stock]["sentiment"]
            )
            stock_mentions[stock]["sentiment"] = round(
                normalize_score(avg_sentiment), 2
            )

    return stock_mentions


def get_reddit_analysis(
    subreddits: list,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
) -> dict:
    """
    Perform sentiment analysis on Reddit posts from specified subreddits and
    categorize stocks based on their sentiment scores.

    Parameters:
        subreddits (list): A list of subreddit names to fetch posts from.
        limit (int): The maximum number of posts to retrieve for each subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.

    Returns:
        dict: A dictionary containing the categorized stocks as 'top_stocks',
              'worst_stocks', and 'rising_stocks', each represented as a list of tuples
              with stock symbol and associated sentiment data.
    """

    posts = get_reddit_posts(subreddits, limit, comment_limit, post_type, time_filter)
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


def get_stock_analysis(
    subreddits: list,
    stocks: list,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
) -> dict:
    """
    Perform sentiment analysis on Reddit posts from specified subreddits for a
    specific set of stocks.

    Parameters:
        subreddits (list): A list of subreddit names to fetch posts from.
        stocks (list): A list of stock symbols to retrieve sentiment data for.
        limit (int): The maximum number of posts to retrieve for each subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.

    Returns:
        dict: A dictionary containing the sentiment data for the specified stocks.
    """

    posts = get_reddit_posts(subreddits, limit, comment_limit, post_type, time_filter)
    stock_data = extract_stock_mentions(posts)

    specific_stock_mentions = {"specific_stock": []}

    for s in stock_data:
        if s in stocks:
            specific_stock_mentions["specific_stock"].append(
                (
                    s,
                    {
                        "count": stock_data[s]["count"],
                        "sentiment": stock_data[s]["sentiment"],
                        "post": stock_data[s]["post"],
                    },
                )
            )

    return specific_stock_mentions


# Main functions for general and specific analysis
def general_reddit_analysis(
    subreddits: list,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
) -> dict:
    """
    Perform general sentiment analysis on Reddit posts from specified subreddits.

    Parameters:
        subreddits (list): A list of subreddit names to fetch posts from.
        limit (int): The maximum number of posts to retrieve for each subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.

    Returns:
        dict: A dictionary containing categorized stocks into 'top_stocks', 'worst_stocks', and 'rising_stocks'.
    """

    return get_reddit_analysis(subreddits, limit, comment_limit, post_type, time_filter)


def specific_stock_analysis(
    subreddits: list,
    stocks: list,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
) -> dict:
    """
    Perform sentiment analysis on Reddit posts from specified subreddits for a
    specific set of stocks.

    Parameters:
        subreddits (list): A list of subreddit names to fetch posts from.
        stocks (list): A list of stock symbols to retrieve sentiment data for.
        limit (int): The maximum number of posts to retrieve for each subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.

    Returns:
        dict: A dictionary containing the sentiment data for the specified stocks.
    """

    return get_stock_analysis(
        subreddits, stocks, limit, comment_limit, post_type, time_filter
    )
