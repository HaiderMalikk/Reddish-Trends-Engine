""" 
This file runs the flask server for the market sentiment analysis app
it has one endpoint /api/home which supports POST requests for processing data
it has 2 main request types:
- getgeneralanalysis: returns the cached analysis if available, otherwise performs fresh analysis
- redogeneralanalysis: performs fresh analysis and updates the cache for all users, so when a user makes a getgeneralanalysis request it gives the latest analysis
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from market_sentiment_analysis import run_general_analysis, run_specific_stock_analysis
from data_processing import get_top_stock, get_worst_stock, get_rising_stock
from gpt_processing import analyze_stock_data_with_gpt
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

print("Flask Server Running")

# Global variable to store the cached analysis results
cached_analysis = None
CACHE_FILE = "cached_analysis.json"

def load_cached_analysis():
    """Load cached analysis from file if it exists"""
    global cached_analysis
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cached_analysis = json.load(f)
                print(f"Loaded cached analysis from {CACHE_FILE}")
        except Exception as e:
            print(f"Error loading cached analysis: {e}")
            cached_analysis = None

def save_cached_analysis(analysis_data):
    """Save analysis data to cache file"""
    global cached_analysis
    cached_analysis = analysis_data
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(analysis_data, f)
            print(f"Saved cached analysis to {CACHE_FILE}")
    except Exception as e:
        print(f"Error saving cached analysis: {e}")

def perform_general_analysis():
    """Perform the general analysis and return the processed data"""
    print(f"Starting scheduled general analysis at {datetime.now()}")
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
    
    # Prepare the response data
    response_data = {"response": {}}
    
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
    
    # Add timestamp to the response
    response_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save the data to cache
    save_cached_analysis(response_data)
    
    print("General analysis completed and cached")
    return response_data

def scheduled_analysis():
    """Function to be called by scheduler"""
    try:
        perform_general_analysis()
        print(f"Scheduled analysis completed at {datetime.now()}")
    except Exception as e:
        print(f"Error in scheduled analysis: {e}")

@app.route("/api/home", methods=["GET", "POST"])
def get_analysis():
    global cached_analysis
    
    if request.method == "POST":
        data = request.get_json()
        print("data received=", data)
        
        request_type = data["request"]["type"]
        
        if request_type == "getgeneralanalysis":
            # Return cached analysis if available, otherwise perform fresh analysis
            if cached_analysis:
                print("Returning cached analysis")
                return jsonify(cached_analysis)
            else:
                print("No cached analysis available, performing fresh analysis")
                return jsonify(perform_general_analysis())
                
        elif request_type == "redogeneralanalysis":
            # Perform fresh analysis and update the cache for all users
            print("Performing fresh analysis as requested by user")
            analysis_result = perform_general_analysis()
            # The perform_general_analysis function already saves to cache,
            # but we'll set it explicitly here as well for clarity
            save_cached_analysis(analysis_result)
            print("Analysis redone and cache updated for all users")
            return jsonify(analysis_result)
            
    elif request.method == "GET":
        print("GET request received. Returning default response.")
        return jsonify({
            "message": "This endpoint supports POST requests for processing data.",
        })

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_analysis, 
                  trigger='cron', 
                  hour=0, 
                  minute=0, 
                  timezone=pytz.timezone('US/Eastern'))

# Load any existing cached analysis on startup
load_cached_analysis()

# Start the scheduler
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True, port=8080)  # TODO turn of debug

# Run the app
# python3 main.py
