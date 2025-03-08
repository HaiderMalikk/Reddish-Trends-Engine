"""
This module contains functions for processing market sentiment analysis data.
The get_top_stock, get_worst_stock, and get_rising_stock functions are used to
extract the top, worst, and rising stocks from the analysis results.

All three functions use a 3-step filter to find the top, worst, and rising stocks:
1. Get all the stocks in each subreddit that have the highest or lowest sentiment.
2. Find the stocks that have appeared multiple times in the top or worst sentiment stocks.
3. Sort the most frequent stocks by the number of mentions in their subreddit.

To understand steps 2 and 3 take these 2 examples:
EX 1) say AAPL and TSAL both appear 3 times with AAPL count = 4 and TSAL count = 1 in the top sentiment stocks. than after step 2 what do we return?
well we use the count. the count tells us how many times the stock was mentioned in the subreddit where it was found. so we return AAPL count = 4.
IDEA: we rank based on sentiment but when a stock has the same sentiment as another and apperes the same number of times in the top or worst sentiment stocks
we rank based on the number of times it was mentioned in the subreddit where it was found.

EX 2)
Top stock:  {'symbol': '$SPY', 'count': 2, 'sentiment': 8.7155, 'price': 576.68, 'high': 580.21, 'low': 572.25, 'change': -3.03, 'percentage_change': -1.21, 'rsi': 28.53}
Worst stock:  {'symbol': '$WMT', 'count': 1, 'sentiment': -4.482, 'price': 95.27, 'high': 97.05, 'low': 95.13, 'change': -0.49, 'percentage_change': -2.38, 'rsi': 35.97}
Rising stock:  [{'symbol': '$SPY', 'count': 2, 'sentiment': 8.7155, 'price': 576.68, 'high': 580.21, 'low': 572.25, 'change': -3.03, 'percentage_change': -1.21, 'rsi': 28.53},
{'symbol': '$GPRO', 'count': 2, 'sentiment': 8.885, 'price': 0.71, 'high': 0.72, 'low': 0.68, 'change': -0.0, 'percentage_change': -2.37, 'rsi': 37.59},
{'symbol': '$OPEN', 'count': 1, 'sentiment': 9.957, 'price': 1.23, 'high': 1.23, 'low': 1.12, 'change': 0.08, 'percentage_change': 1.24, 'rsi': 41.24}]

In this example, the top stock is $SPY, which has a sentiment of 8.7155 and appears 2 times in the top sentiment stocks.
But OPEN has a higher sentiment of 9.957 but since it only appears 1 time in the top sentiment stocks it is not the top stock.
But still is a rising stock because it has the highest
"""


def get_top_stock(analysis: list[dict]) -> dict | None:
    """
    Perform a 3 step filter to get the top stock from a subreddits analysis.
    - 3 step filter
    1) get all the stocks in each subreddit that have the highest sentiment
    2) get all the stocks that have appeare multiple times in the top sentiment stocks
    3) do a final sort on these top reappearing stocks by the number of mentions it has in its subreddit

    Parameters:
        analysis (list[dict]): A list containing a dictionary for each subreddit, with the analysis results for that subreddit.

    Returns:
        dict: A dictionary containing information about the top stock. if there are no top stocks return None
    """
    # get all the stocks in each subreddit from top stocks that have the highest sentiment
    # the stocks are already sorted by sentiment in descending order but there are usually multiple stocks with the same sentiment
    top_sentiment_stocks = []
    for result in analysis:
        subreddit = list(result.keys())[
            0
        ]  # get just the subreddit name from the dictionary key
        if not result[subreddit]["top_stocks"]:  # Check if there are any top stocks
            continue
        max_sentiment = result[subreddit]["top_stocks"][0]["sentiment"]
        top_sentiment_stocks.extend(
            stock
            for stock in result[subreddit]["top_stocks"]
            if stock["sentiment"] == max_sentiment
        )

    if not top_sentiment_stocks:
        return None  # Return None if no stocks found

    # from the top sentiment stocks count how many times each stock appears in the top_sentiment_stocks list
    stock_counts = {}
    for stock in top_sentiment_stocks:
        symbol = stock["symbol"]
        if symbol in stock_counts:
            stock_counts[symbol] += 1
        else:
            stock_counts[symbol] = 1

    # From the most frequent stocks find the stock with the highest mention count which in the ammount of times it appears in one subreddit
    max_appearances = max(stock_counts.values()) if stock_counts else 0
    most_frequent_stocks = [
        stock
        for stock in top_sentiment_stocks
        if stock_counts[stock["symbol"]] == max_appearances
    ]

    # Return the stock with the highest mention count among the most frequent ones
    return (
        max(most_frequent_stocks, key=lambda c: c["count"])
        if most_frequent_stocks
        else None
    )


def get_worst_stock(analysis: list[dict]) -> dict | None:
    """
    Perform a 3 step filter to get the worst stock from a subreddits analysis.
    - 3 step filter
    1) get all the stocks in each subreddit that have the lowest sentiment
    2) get all the stocks that have appeared multiple times in the worst sentiment stocks
    3) do a final sort on these worst reappearing stocks by the number of mentions it has in its subreddit

    Parameters:
        analysis (list[dict]): A list containing a dictionary for each subreddit, with the analysis results for that subreddit.

    Returns:
        dict: A dictionary containing information about the worst stock. if there are no worst stocks return None
    """
    # get all the stocks in each subreddit from bottom stocks that have the lowest sentiment
    # the stocks are already sorted by sentiment in descending order but there are usually multiple stocks with the same sentiment
    worst_sentiment_stocks = []
    for result in analysis:
        subreddit = list(result.keys())[
            0
        ]  # get just the subreddit name from the dictionary key
        if not result[subreddit]["worst_stocks"]:  # Check if there are any worst stocks
            continue
        min_sentiment = result[subreddit]["worst_stocks"][-1]["sentiment"]
        worst_sentiment_stocks.extend(
            stock
            for stock in result[subreddit]["worst_stocks"]
            if stock["sentiment"] == min_sentiment
        )

    if not worst_sentiment_stocks:
        return None  # Return None if no stocks found

    # from the worst sentiment stocks count how many times each stock appears in the worst_sentiment_stocks list
    stock_counts = {}
    for stock in worst_sentiment_stocks:
        symbol = stock["symbol"]
        if symbol in stock_counts:
            stock_counts[symbol] += 1
        else:
            stock_counts[symbol] = 1

    # From the most frequent stocks find the stock with the highest mention count which in the ammount of times it appears in one subreddit
    max_appearances = max(stock_counts.values()) if stock_counts else 0
    most_frequent_stocks = [
        stock
        for stock in worst_sentiment_stocks
        if stock_counts[stock["symbol"]] == max_appearances
    ]

    # Return the stock with the highest mention count among the most frequent ones
    return (
        max(most_frequent_stocks, key=lambda c: c["count"])
        if most_frequent_stocks
        else None
    )


def get_rising_stock(analysis: list[dict], limit:int = 1) -> list[dict] | None:
    """
    Perform a 3 step filter to get the rising stocks from a subreddits analysis.
    - 3 step filter
    1) get all the stocks in each subreddit that have the highest sentiment
    2) get all the stocks that have appeared multiple times in the rising sentiment stocks
    3) do a final sort on these rising reappearing stocks by the number of mentions it has in its subreddit and get the top 3

    Parameters:
        analysis (list[dict]): A list containing a dictionary for each subreddit, with the analysis results for that subreddit.
        limit (int): The maximum number of rising stocks to return.

    Returns:
       list[dict]: A list of length limit containing information in dictionary form about rising stocks sorted in descending order. if there are no rising stocks return None
    """
    # get all the stocks in each subreddit that have the highest sentiment
    # the stocks are already sorted by sentiment in descending order but there are usually multiple stocks with the same sentiment
    rising_sentiment_stocks = []
    for result in analysis:
        subreddit = list(result.keys())[
            0
        ]  # get just the subreddit name from the dictionary key
        if not result[subreddit][
            "rising_stocks"
        ]:  # Check if there are any rising stocks
            continue
        max_sentiment = result[subreddit]["rising_stocks"][0]["sentiment"]
        rising_sentiment_stocks.extend(
            stock
            for stock in result[subreddit]["rising_stocks"]
            if stock["sentiment"] == max_sentiment
        )

    if not rising_sentiment_stocks:
        return None  # Return None if no stocks found

    # from the rising sentiment stocks count how many times each stock appears in the rising_sentiment_stocks list
    stock_counts = {}
    for stock in rising_sentiment_stocks:
        symbol = stock["symbol"]
        if symbol in stock_counts:
            stock_counts[symbol] += 1
        else:
            stock_counts[symbol] = 1

    # From the most frequent stocks find the stock with the highest mention count which in the ammount of times it appears in one subreddit
    max_appearances = max(stock_counts.values()) if stock_counts else 0
    most_frequent_stocks = [
        stock
        for stock in rising_sentiment_stocks
        if stock_counts[stock["symbol"]] == max_appearances
    ]

    # Return 3 of the stock with the highest mention count among the most frequent ones
    return (
        sorted(most_frequent_stocks, key=lambda c: c["count"], reverse=True)[:3]
        if most_frequent_stocks
        else None
    )
