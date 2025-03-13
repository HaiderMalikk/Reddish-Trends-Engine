from market_sentiment_analysis import run_general_analysis, run_specific_stock_analysis
from data_processing import get_top_stock, get_worst_stock, get_rising_stock
from gpt_processing import analyze_stock_data_with_gpt

# Define the subreddits to analyze
subreddits = ["wallstreetbets", "stocks", "stockmarket"]

# gebeneral stock analysis'
# run the specific stock analysis
specific_stock_analysis = run_specific_stock_analysis(subreddits, ["$GOGO", "$ASAN"], 1, 1, "hot", "1mo")

# print the results
print("specific_stock_analysis:", specific_stock_analysis)