from market_sentiment_analysis import run_analysis

analysis = run_analysis(
    subreddits=[
        "wallstreetbets",
        "stocks",
        "StocksAndTrading",
    ],  # List of subreddits to analyze
    limit=10,  # Maximum number of posts to retrieve,
    stock_data_period="1mo",  # Period for which to fetch stock data
)


def get_top_stock(analysis: list[dict]) -> dict:
    """
    Perform a 3 step filter to get the top stock from a subreddits analysis.
    - 3 step filter
    1) get all the stocks in each subreddit that have the highest sentiment
    2) get all the stocks that have mentions in multiple subreddits from the stocks with the same max sentiment
    3) do a final sort on these top stocks by the number of mentions it has in a single subreddit

    Parameters:
        analysis (list[dict]): A list containing a dictionary for each subreddit, with the analysis results for that subreddit.

    Returns:
        list[dict]: A list containing a dictionary for each subreddit, with the analysis results for that subreddit.
    """
    # get all the stocks in each subreddit that have the highest sentiment
    # the stocks are already sorted by sentiment in descending order but there are usually multiple stocks with the same sentiment
    top_sentiment_stocks = []
    for result in analysis:
        subreddit = str(result.keys())[12:-3]
        max_sentiment = result[subreddit]["top_stocks"][0]["sentiment"]
        top_sentiment_stocks.extend(
            stock
            for stock in result[subreddit]["top_stocks"]
            if stock["sentiment"] == max_sentiment
        )

    # get all the stocks that have mentions in multiple subreddits from the stocks with the same max sentiment
    # if a stock has mentions in multiple subreddits, it is likely to be a good stock
    seen = []
    mention_count = [0] * len(top_sentiment_stocks)
    for index, stock in enumerate(top_sentiment_stocks):
        if stock["symbol"] in seen:
            mention_count[index] += 1
        else:
            seen.append(stock["symbol"])

    # do a final sort on these top stocks by the number of mentions it has
    # i.e both TSLA and AAPL have 2 top stock mentions across 2 subreddits, but TSLA has a higher count
    # meaning tesla has more mentions in the subreddit it was fount in then its the top stock
    filtered_top_stocks = []
    max_mentions = max(mention_count)
    filtered_top_stocks.extend(
        top_sentiment_stocks[index]
        for index in range(len(mention_count))
        if mention_count[index] == max_mentions
    )
    return max(
        filtered_top_stocks, key=lambda c: c["count"]
    )  # top stock is the one with the highest count

print("analysis: ", analysis)
print("Top stock: ",get_top_stock(analysis))
