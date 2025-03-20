"""
This file runs sentiment analysis on Reddit data for a given list of subreddits
and a specific stock symbol. It uses the general_reddit_analysis and
specific_stock_analysis functions from the reddit_analysis module to perform
the analysis.

- It uses the concurrent.futures module to run the analysis functions in parallel.
- This reduces the time for 2 10 post reddit analysis from 50 seconds to 30 seconds as they dont run one after the other.
- each new subreddit analysis for 10 post will take a max of 30 seconds no matter how many subreddits are added.

- it also uses yaspin for spinner to show the progress of the analysis.
- The spinner will show when the analysis is running and will stop when the analysis is completed.
"""

from sentiment_analysis import general_reddit_analysis, specific_stock_analysis
from market_analysis import merge_stock_data
import concurrent.futures


def general_stock_and_social_analysis(
    subreddit: str,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
    stock_period: str,
) -> dict:
    """
    Perform a general sentiment analysis on a subreddit and a financial analysis from those results.

    Parameters:
        subreddit (str): The subreddit to analyze.
        limit (int): The maximum number of posts to retrieve for each subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.
        stock_period (str): The period of time to retrieve stock data for. Options are "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", and "ytd".

    Returns:
        dict: A dictionary with the subreddit as the key and the financial data as the value.
    """
    general_analysis = general_reddit_analysis(
        subreddit, limit, comment_limit, post_type, time_filter
    )
    financial_data = merge_stock_data(general_analysis, stock_period)

    return {subreddit: financial_data}


def specific_stock_and_social_analysis(
    subreddit: str,
    stocks: list,
    limit: int,
    comment_limit: int,
    post_type: str,
    time_filter: str | None,
    stock_period: str,
) -> dict:
    """
    Perform sentiment analysis on a subreddit for a specific set of stocks and
    merge the results with financial stock data.

    Parameters:
        subreddit (str): The subreddit to analyze.
        stocks (list): A list of stock symbols to analyze.
        limit (int): The maximum number of posts to retrieve from the subreddit.
        comment_limit (int): The maximum number of comments to retrieve per post.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied.
        stock_period (str): The period of time to retrieve stock data for. Options are "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", and "ytd".

    Returns:
        dict: A dictionary with the subreddit as the key and the merged financial data as the value.
    """
    specific_analysis = specific_stock_analysis(
        subreddit, stocks, limit, comment_limit, post_type, time_filter
    )

    financial_data = merge_stock_data(specific_analysis, stock_period)

    return {subreddit: financial_data}


def run_general_analysis(
    subreddits: list,
    limit: int = 10,
    comment_limit: int = 10,
    post_type: str = "hot",
    time_filter: str | None = None,
    stock_period: str = "1mo",
) -> list[dict]:
    """
    Run a general sentiment analysis on a list of subreddits and merge the results
    with financial stock data.

    Parameters:
        subreddits (list): A list of subreddit names to analyze.
        limit (int): The maximum number of posts to retrieve for each subreddit. Defaults to 10.
        comment_limit (int): The maximum number of comments to retrieve per post. Defaults to 10.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial". Defaults to "hot".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied. Defaults to None.
        stock_period (str): The period of time to retrieve stock data for. Options are "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", and "ytd". Defaults to "1mo".

    Returns:
        list[dict]: A list of dictionaries with the subreddit as the key and the merged financial data as the value.
    """
    results = []  # Store the results of each subreddit analysis

    # Run sentiment analysis in parallel on each subreddit
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print("📈 Sentiment Analysis in progress...")
        futures = []
        futures.extend(
            executor.submit(
                general_stock_and_social_analysis,
                subreddit,
                limit,
                comment_limit,
                post_type,
                time_filter,
                stock_period,
            )
            for subreddit in subreddits
        )
        results.extend(future.result() for future in futures)
        print("✅ Sentiment Analysis completed!")
    return results


def run_specific_stock_analysis(
    subreddits: list,
    stocks: list,
    limit: int = 10,
    comment_limit: int = 10,
    post_type: str = "hot",
    time_filter: str | None = None,
    stock_period: str = "1mo",
) -> list[dict]:
    """
    Run a sentiment analysis on a list of subreddits for a specific set of stocks and
    merge the results with financial stock data.

    Parameters:
        subreddits (list): A list of subreddit names to analyze.
        stocks (list): A list of stock symbols to analyze.
        limit (int): The maximum number of posts to retrieve for each subreddit. Defaults to 10.
        comment_limit (int): The maximum number of comments to retrieve per post. Defaults to 10.
        post_type (str): The type of posts to retrieve. Options are "hot", "new", "top", "rising", and "controversial". Defaults to "hot".
        time_filter (str | None): The time filter for top and controversial posts. Options are "hour", "day", "week", "month", "year", and "all". If None, no time filter is applied. Defaults to None.
        stock_period (str): The period of time to retrieve stock data for. Options are "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", and "ytd". Defaults to "1mo".

    Returns:
        list[dict]: A list of dictionaries with the subreddit as the key and the merged financial data as the value.
    """
    results = []  # Store the results of each subreddit analysis

    # Run sentiment analysis in parallel on each subreddit
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print("📈 Sentiment Analysis in progress...")
        futures = []
        futures.extend(
            executor.submit(
                specific_stock_and_social_analysis,
                subreddit,
                stocks,
                limit,
                comment_limit,
                post_type,
                time_filter,
                stock_period,
            )
            for subreddit in subreddits
        )
        results.extend(future.result() for future in futures)
        print("✅ Sentiment Analysis completed!")

    return results
