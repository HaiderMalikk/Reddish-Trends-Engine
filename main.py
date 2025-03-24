"""
This module sets up a Flask web server that provides endpoints for stock market sentiment analysis.
It integrates with various analysis functions to perform general and specific stock analyses,
caches the results, and schedules periodic updates using APScheduler.
Key functionalities include:
- Performing general stock market sentiment analysis based on subreddit data.
- Performing specific stock analysis based on user-defined parameters.
- Caching analysis results to improve performance and reduce redundant computations.
- Providing endpoints for retrieving cached analysis or triggering fresh analyses.
- Scheduling periodic analysis updates to keep the cache up-to-date.
- Handling customizable analysis requests via a playground endpoint.
Modules and libraries used:
- Flask: For creating the web server and handling HTTP requests.
- Flask-CORS: For enabling Cross-Origin Resource Sharing.
- APScheduler: For scheduling periodic tasks.
- Various custom modules (market_sentiment_analysis, data_processing, gpt_processing) for performing the actual analysis.
Endpoints:
- /api/home: Handles GET and POST requests for general analysis of stock data.
- /api/playground: Handles POST requests for customizable stock analysis based on user-defined parameters.
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
CORS(app, origins=["https://www.reddishtrends.com"])

ALLOWED_ORIGINS = {"https://www.reddishtrends.com"}  # Allowed domains

@app.before_request
def check_origin():
    """Manually enforce allowed origins for ALL requests."""
    origin = request.headers.get("Origin")  # Get the request's Origin header
    if origin and origin not in ALLOWED_ORIGINS:
        return jsonify({"error": "Unauthorized origin"}), 403
    """ block postman curl etc """
    referer = request.headers.get("Referer")
    if not referer or "reddishtrends.com" not in referer:
        return jsonify({"error": "Forbidden"}), 403

print("Flask Server Running")

# Global variable to store the cached analysis results
cached_analysis = None
CACHE_FILE = "cached_analysis.json"


def load_cached_analysis():
    """Load cached analysis from file if it exists"""
    global cached_analysis
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached_analysis = json.load(f)
                print(f"Loaded cached analysis from {CACHE_FILE}")
        except Exception as e:
            print(f"Error loading cached analysis: {e}")
            cached_analysis = None


def is_cache_outdated():
    """Check if cached analysis is outdated (more than 24 hours old)"""
    if not cached_analysis or "last_updated" not in cached_analysis:
        return True

    try:
        last_updated = datetime.strptime(
            cached_analysis["last_updated"], "%Y-%m-%d %H:%M:%S"
        )
        current_time = datetime.now()
        diff = current_time - last_updated

        # Return True if more than 24 hours have passed
        return diff.total_seconds() > 24 * 60 * 60
    except Exception as e:
        print(f"Error checking cache age: {e}")
        return True


def save_cached_analysis(analysis_data):
    """Save analysis data to cache file"""
    global cached_analysis
    cached_analysis = analysis_data
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(analysis_data, f)
            print(f"Saved cached analysis to {CACHE_FILE}")
    except Exception as e:
        print(f"Error saving cached analysis: {e}")


def perform_general_analysis():
    """Perform the general analysis and return the processed data"""
    print(f"Starting scheduled general analysis at {datetime.now()}")
    subreddits = ["wallstreetbets", "stocks", "stockmarket"]

    # Run the general analysis
    general_analysis = run_general_analysis(subreddits, 100)

    # get the top stock, worst stock and rising stock
    top_stock = get_top_stock(general_analysis)
    worst_stock = get_worst_stock(general_analysis)
    # Add a safety check for rising stocks
    rising_stocks = get_rising_stock(general_analysis)
    # Initialize rising_stock to None by default
    rising_stock = None
    if rising_stocks:
        if len(rising_stocks) > 1:
            rising_stock = rising_stocks[1]  # Get second rising stock to avoid overlap
        elif len(rising_stocks) > 0:
            rising_stock = rising_stocks[0]  # Only one rising stock available

    # Analyze the top, worst and rising stocks with GPT if available
    top_gpt_analysis = analyze_stock_data_with_gpt(top_stock) if top_stock else None
    worst_gpt_analysis = (
        analyze_stock_data_with_gpt(worst_stock) if worst_stock else None
    )
    rising_gpt_analysis = (
        analyze_stock_data_with_gpt(rising_stock) if rising_stock else None
    )

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


def perform_playground_general_analysis(parameters):
    """
    Perform a customizable general analysis based on provided parameters
    No caching is done for playground results
    """
    subreddits = parameters.get(
        "subreddits", ["wallstreetbets", "stocks", "stockmarket"]
    )
    limit = int(parameters.get("limit", 10))
    comment_limit = int(parameters.get("comment_limit", 10))
    sort = parameters.get("sort", "hot")
    time = parameters.get("time", None)
    period = parameters.get("period", "1mo")

    # signal from frontend to set time to None further checks done in sentiment_analysis.py but this is a workaround
    if time == "none":
        time = None

    print(
        f"Running playground general analysis with: subreddits={subreddits}, limit={limit}, comment_limit={comment_limit}, sort={sort}, time={time}, period={period}"
    )

    # Run the general analysis with custom parameters
    general_analysis = run_general_analysis(
        subreddits, limit, comment_limit, sort, time, period
    )

    # Process the results
    response_data = {
        "analysis_results": general_analysis,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return response_data


def perform_playground_specific_analysis(parameters):
    """
    Perform a customizable specific stock analysis based on provided parameters
    No caching is done for playground results
    """
    subreddits = parameters.get(
        "subreddits", ["wallstreetbets", "stocks", "stockmarket"]
    )
    stocks = parameters.get("stocks", ["$AAPL", "$TSLA"])
    limit = int(parameters.get("limit", 10))
    comment_limit = int(parameters.get("comment_limit", 10))
    sort = parameters.get("sort", "hot")
    time = parameters.get("time", None)
    period = parameters.get("period", "1mo")

    # signal from frontend to set time to None further checks done in sentiment_analysis.py but this is a workaround
    if time == "none":
        time = None

    print(
        f"Running playground specific analysis with: subreddits={subreddits}, stocks={stocks}, limit={limit}, comment_limit={comment_limit}, sort={sort}, time={time}, period={period}"
    )

    # Run the specific stock analysis with custom parameters
    specific_analysis = run_specific_stock_analysis(
        subreddits, stocks, limit, comment_limit, sort, time, period
    )

    # Process the results
    response_data = {
        "analysis_results": specific_analysis,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return response_data


@app.route("/api/playground", methods=["POST"])
def playground_analysis():
    """
    Endpoint for playground analysis requests.
    Supported request types:
    - getplaygroundgeneralanalysis: Perform a general sentiment analysis with custom parameters
    - getplaygroundspecificanalysis: Perform a specific stock sentiment analysis with custom parameters
    Returns analysis results as a JSON object
    """
    if request.method == "POST":
        try:
            data = request.get_json()
            print("Playground data received:", data)

            if not data or "request" not in data or "type" not in data["request"]:
                return jsonify({"error": "Invalid request format"}), 400

            request_type = data["request"]["type"]
            parameters = data["request"].get("parameters", {})

            if request_type == "getplaygroundgeneralanalysis":
                print("Processing playground general analysis request")
                result = perform_playground_general_analysis(parameters)
                return jsonify(result)

            elif request_type == "getplaygroundspecificanalysis":
                print("Processing playground specific stock analysis request")
                result = perform_playground_specific_analysis(parameters)
                return jsonify(result)

            else:
                return jsonify({"error": f"Unknown request type: {request_type}"}), 400

        except Exception as e:
            print(f"Error processing playground request: {str(e)}")
            return jsonify({"error": f"Error processing request: {str(e)}"}), 500

    return jsonify({"error": "Method not allowed"}), 405


@app.route("/api/home", methods=["GET", "POST"])
def get_analysis():
    """
    Endpoint to handle GET and POST requests for general analysis of stock data.

    POST requests:
    - "getgeneralanalysis": Returns the cached analysis if available, otherwise performs a fresh analysis.
    - "redogeneralanalysis": Performs a fresh analysis and updates the cache for all users.

    GET requests:
    - Returns a default response with a message indicating that this endpoint supports POST requests for processing data.
    """
    global cached_analysis

    if request.method == "POST":
        data = request.get_json()
        print("data received=", data)

        request_type = data["request"]["type"]

        if request_type == "getgeneralanalysis":
            # Check if cache is outdated
            if cached_analysis and not is_cache_outdated():
                print("Returning cached analysis")
                return jsonify(cached_analysis)
            else:
                if not cached_analysis:
                    print("No cached analysis available, performing fresh analysis")
                else:
                    print("Cached analysis is outdated, performing fresh analysis")
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
        return jsonify(
            {
                "message": "This endpoint supports POST requests for processing data.",
            }
        )


def startup_cache_update():
    """Check if the cache is outdated on server startup and update if needed"""
    print("Checking if cache needs updating on startup...")
    if is_cache_outdated():
        print("Cache is outdated or missing, performing fresh analysis on startup")
        perform_general_analysis()
    else:
        print("Cache is still valid, no need for immediate update")


""" 
- Cron job
- The application uses APScheduler to schedule periodic tasks.
- Two types of jobs are scheduled: a daily cron job and an interval job as a fallback.
1. Daily Cron Job:
    - Function: `scheduled_analysis`
    - Trigger: Cron
    - Schedule: Every day at 12:00 PM (noon) Eastern Time
    - Timezone: US/Eastern
    - Purpose: To perform a general stock market sentiment analysis and update the cache with the latest results.
2. Interval Job (Fallback):
    - Function: `scheduled_analysis`
    - Trigger: Interval
    - Schedule: Every 24 hours
    - Purpose: To ensure that the analysis runs at least once every 24 hours, acting as a fallback in case the server restarts and misses the cron job.
3. Startup Cache Update:
    - Function: `startup_cache_update`
    - Trigger: Date
    - Schedule: Runs immediately on server startup
    - Purpose: To check if the cache is outdated on server startup and perform a fresh analysis if needed.
Additional Details:
- The scheduler is initialized with `daemon=True` to ensure it runs in the background.
- The scheduler is started with `scheduler.start()`.
- The scheduler is shut down gracefully when the application exits using `atexit.register(lambda: scheduler.shutdown())`.
"""

# Initialize scheduler with more reliable approach
scheduler = BackgroundScheduler(daemon=True)
# Run every day at 12:00 PM (noon) Eastern Time
scheduler.add_job(
    func=scheduled_analysis,
    trigger="cron",
    hour=12,
    minute=00,
    timezone=pytz.timezone("US/Eastern"),
)

# Also add an interval job as a fallback to ensure analysis runs at least once every 24 hours
# This helps when the server restarts and might have missed the cron job
scheduler.add_job(
    func=scheduled_analysis,
    trigger="interval",
    hours=24,
)

# on startup check if cache is outdated
scheduler.add_job(
    func=startup_cache_update,
    trigger="date",
    run_date=datetime.now(),  # Explicitly set to run immediately
)

# Load any existing cached analysis on startup
load_cached_analysis()

# Run startup check immediately rather than relying on scheduler
startup_cache_update()

# Start the scheduler
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# this is the main function that runs the app
if __name__ == "__main__":
    app.run(port=5000)