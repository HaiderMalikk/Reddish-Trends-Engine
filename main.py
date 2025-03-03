# simple flask test app
from flask import Flask
from market_sentiment_analysis import sentiment_analysis

app = Flask(__name__)


@app.route("/")
def hello():
    analysis = sentiment_analysis(
        subreddits=[
            "wallstreetbets",
            "stocks",
            "StocksAndTrading",
        ],  # List of subreddits to analyze
        limit=10,  # Maximum number of posts to retrieve,
        stock_data_period="1mo",  # Period for which to fetch stock data
    )

    return "Analysis completed!" + str(analysis)


if __name__ == "__main__":
    app.run()

# Run the app
# python3 main.py
