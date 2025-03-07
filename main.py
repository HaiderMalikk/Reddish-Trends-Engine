# simple flask test app
from flask import Flask, request, jsonify
from flask_cors import CORS
from market_sentiment_analysis import run_general_analysis, run_specific_stock_analysis
from data_processing import get_top_stock, get_worst_stock, get_rising_stock
from gpt_processing import analyze_stock_data_with_gpt

app = Flask(__name__)
CORS(app)

print("Flask Server Running")

# TODO: add 2 endpoints one for live srching stock i.e genral or specific analysis and one for stock of the day clac at 00:00 EST no re calc just return stored json data (see gpt chat for it) uses 2 end points
# TODO deploy on heroku.


@app.route("/api/home", methods=["GET", "POST"])
def get_analysis():
    response_data = {}

    if request.method == "POST":
        data = request.get_json()
        print("data=", data)

        request_type = data["request"]["type"]
        if request_type == "getgeneralanalysis":
            response_data = {
                "response": {
                    "Top Stock": {
                        "symbol": "$COST",
                        "count": 1,
                        "sentiment": 6.369,
                        "post": "Sigma Sigma on the wall",
                        "price": 1026.62,
                        "high": 1045.89,
                        "low": 1019.05,
                        "change": -5.52,
                        "percentage_change": -2.02,
                        "rsi": 36.08,
                        "GPT_Analysis": {
                            "overview": "Costco ($COST) has experienced a slight decline of 2.02% in its stock price, closing at $1026.62 after reaching a high of $1045.89 and a low of $1019.05.",
                            "market_sentiment": "The sentiment score of 6.369 indicates a moderately positive outlook among investors, despite the recent price drop. The post suggests confidence in the market, which may reflect a bullish sentiment overall.",
                            "technical_analysis": "The RSI of 36.08 suggests that the stock is nearing oversold territory (below 30), indicating potential for a rebound. However, the recent downward trend could signal caution for short-term traders.",
                            "fundamental_analysis": "Costco is generally considered a strong company with solid fundamentals; however, specific financial metrics such as revenue growth, profit margins, and debt levels are not provided in this data. Investors should consider these factors when assessing long-term viability.",
                            "prediction": "Given the current RSI and market sentiment, there is potential for a short-term recovery in the stock price if buying interest increases. However, caution is advised due to the recent downtrend.",
                            "Confidence Score": 70,
                        },
                    }
                }
            }

    elif request.method == "GET":
        print("GET request received. Returning default response.")
        response_data = {
            "message": "This endpoint supports POST requests for processing data.",
        }

    print("Response Data:", response_data)
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True, port=8080)  # TODO turn of debug

# Run the app
# python3 main.py
