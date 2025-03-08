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
        print("data received=", data)
        subreddits = ["wallstreetbets", "stocks", "stockmarket"]        
        # Run the general analysis
        general_analysis = run_general_analysis(subreddits, limit=50)
        # get the top stock, worst stock and rising stock
        top_stock = get_top_stock(general_analysis)
        worst_stock = get_worst_stock(general_analysis)
        rising_stock = get_rising_stock(general_analysis)[1] # just get the second rising stock to avoid overlap with top stock
        
        # Check if stocks are valid dictionaries before analyzing
        top_gpt_analysis = analyze_stock_data_with_gpt(top_stock) if top_stock else None
        worst_gpt_analysis = analyze_stock_data_with_gpt(worst_stock) if worst_stock else None
        rising_gpt_analysis = analyze_stock_data_with_gpt(rising_stock) if rising_stock else None
        
        request_type = data["request"]["type"]
        if request_type == "getgeneralanalysis":
            response_data = {
                "response": {}
            }
            
            # Handle top stock data
            if not top_stock:
                response_data["response"]["Top_Stock"] = "None"
            else:
                response_data["response"]["Top_Stock"] = {
                    "symbol": top_stock["symbol"],
                    "company_name": top_stock["company_name"], 
                    "count": top_stock["count"],
                    "sentiment": top_stock["sentiment"],
                    "post": top_stock["post"],
                    "price": top_stock["price"],
                    "high": top_stock["high"],
                    "low": top_stock["low"],
                    "change": top_stock["change"],
                    "percentage_change": top_stock["percentage_change"],
                    "rsi": top_stock["rsi"],
                    "GPT_Analysis": {
                        "overview": top_gpt_analysis["overview"],
                        "market_sentiment": top_gpt_analysis["market_sentiment"],
                        "technical_analysis": top_gpt_analysis["technical_analysis"],
                        "fundamental_analysis": top_gpt_analysis["fundamental_analysis"],
                        "prediction": top_gpt_analysis["prediction"],
                        "Confidence Score": top_gpt_analysis["Confidence Score"],
                    },
                }
            
            # Handle worst stock data
            if not worst_stock:
                response_data["response"]["Worst_Stock"] = "None"
            else:
                response_data["response"]["Worst_Stock"] = {
                    "symbol": worst_stock["symbol"],
                    "company_name": worst_stock["company_name"],
                    "count": worst_stock["count"],
                    "sentiment": worst_stock["sentiment"],
                    "post": worst_stock["post"],
                    "price": worst_stock["price"],
                    "high": worst_stock["high"],
                    "low": worst_stock["low"],
                    "change": worst_stock["change"],
                    "percentage_change": worst_stock["percentage_change"],
                    "rsi": worst_stock["rsi"],
                    "GPT_Analysis": {
                        "overview": worst_gpt_analysis["overview"],
                        "market_sentiment": worst_gpt_analysis["market_sentiment"],
                        "technical_analysis": worst_gpt_analysis["technical_analysis"],
                        "fundamental_analysis": worst_gpt_analysis["fundamental_analysis"],
                        "prediction": worst_gpt_analysis["prediction"],
                        "Confidence Score": worst_gpt_analysis["Confidence Score"],
                    },
                }
            
            # Handle rising stock data
            if not rising_stock:
                response_data["response"]["Rising_Stock"] = "None"
            else:
                response_data["response"]["Rising_Stock"] = {
                    "symbol": rising_stock["symbol"],
                    "company_name": rising_stock["company_name"],
                    "count": rising_stock["count"],
                    "sentiment": rising_stock["sentiment"],
                    "post": rising_stock["post"],
                    "price": rising_stock["price"],
                    "high": rising_stock["high"],
                    "low": rising_stock["low"],
                    "change": rising_stock["change"],
                    "percentage_change": rising_stock["percentage_change"],
                    "rsi": rising_stock["rsi"],
                    "GPT_Analysis": {
                        "overview": rising_gpt_analysis["overview"],
                        "market_sentiment": rising_gpt_analysis["market_sentiment"],
                        "technical_analysis": rising_gpt_analysis["technical_analysis"],
                        "fundamental_analysis": rising_gpt_analysis["fundamental_analysis"],
                        "prediction": rising_gpt_analysis["prediction"],
                        "Confidence Score": rising_gpt_analysis["Confidence Score"],
                    },
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
