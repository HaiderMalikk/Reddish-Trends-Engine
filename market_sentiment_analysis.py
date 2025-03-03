"""
This file runs sentiment analysis on Reddit data for a given list of subreddits
and a specific stock symbol. It uses the general_reddit_analysis and
specific_stock_analysis functions from the reddit_analysis module to perform
the analysis.

- It uses the concurrent.futures module to run the analysis functions in parallel.
- This reduces the time for 2 10 post reddit analysis from 50 seconds to 30 seconds.
- each new subreddit analysis for 10 post will take a max of 30 seconds no matter how many subreddits are added.

- it also uses yaspin for spinner to show the progress of the analysis.
- The spinner will show when the analysis is running and will stop when the analysis is completed.
"""

from sentiment_analysis import general_reddit_analysis
from market_analysis import merge_stock_data
import concurrent.futures
from yaspin import yaspin  # using yaspin for spinne


def stock_and_social_analysis(subreddit: str, limit: int) -> dict:
    """
    Perform general Reddit analysis for a subreddit and a financial analysis from those results.

    Parameters:
        subreddit (str): The name of the subreddit to analyze.
        limit (int): The maximum number of posts to retrieve.

    Returns:
        dict: A dictionary containing the analysis results for the subreddit.
    """
    general_analysis = general_reddit_analysis(subreddit, limit)
    financial_data = merge_stock_data(general_analysis)

    return {subreddit: financial_data}


def sentiment_analysis() -> list:
    """
    Run sentiment analysis on the given list of subreddits and return the results.

    Parameters:
        None

    Returns:
        list: A list of dictionaries containing the analysis results for each subreddit.
    """
    subreddits = [
        "wallstreetbets",
        "stocks",
        "StocksAndTrading",
    ]  # List of subreddits to analyze
    limit = 10  # Maximum number of posts to retrieve

    results = []

    # Run sentiment analysis in parallel on each subreddit
    with concurrent.futures.ThreadPoolExecutor() as executor:
        with yaspin(
            text="📈 Sentiment Analysis in progress...", color="red"
        ) as spinner:
            futures = []
            futures.extend(
                executor.submit(stock_and_social_analysis, subreddit, limit)
                for subreddit in subreddits
            )
            for future in futures:
                results.append(future.result())  # Collect results

            spinner.text = "✅ Sentiment Analysis completed!"
            spinner.ok()

    return results


print(sentiment_analysis())  # Run the sentiment analysis
