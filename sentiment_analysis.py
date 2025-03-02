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

from reddit_analysis import general_reddit_analysis
import concurrent.futures
from yaspin import yaspin  # using yaspin for spinner


def reddit_analysis(subreddit, limit):
    # General analysis
    """
    Perform general Reddit analysis for a subreddit.

    Parameters:
        subreddit (str): The name of the subreddit to analyze.
        limit (int): The maximum number of posts to retrieve.

    Prints:
        The general analysis results for the subreddit.
    """

    general_analysis = general_reddit_analysis(subreddit, limit)
    # Print results
    print("\n🚀 General Reddit Analysis:")
    print(f"📊 {subreddit} Analysis:")
    print(general_analysis)

    print("✅ Analysis completed!\n")


def sentiment_analysis():
    """
    Runs sentiment analysis on Reddit data for a given list of subreddits.

    Parameters:
        None

    Prints:
        The sentiment analysis results for each subreddit.
    """
    subreddits = [
        "wallstreetbets",
        "stocks",
        "investing",
    ]  # List of subreddits to analyze
    limit = 10  # Maximum number of posts to retrieve

    with concurrent.futures.ThreadPoolExecutor() as executor:
        with yaspin(
            text="📈 Sentiment Analysis in progress...", color="red"
        ) as spinner:
            futures = []
            for subreddit in subreddits:
                futures.append(executor.submit(reddit_analysis, subreddit, limit))

            for future in futures:
                future.result()  # Wait for the individual future to complete

            spinner.text = "✅ Sentiment Analysis completed!"
            spinner.ok()


sentiment_analysis()  # Run the sentiment analysis
