from market_sentiment_analysis import run_general_analysis, run_specific_stock_analysis
from data_processing import get_top_stock, get_worst_stock, get_rising_stock

# Define the subreddits to analyze
subreddits = ["wallstreetbets", "stocks", "stockmarket"]

# Run the general analysis
general_analysis = run_general_analysis(
    subreddits, limit=10, stock_data_period="1mo"
)
# get the top stock, worst stock and rising stock
top_stock = get_top_stock(general_analysis)
worst_stock = get_worst_stock(general_analysis)
rising_stock = get_rising_stock(general_analysis)

# run the specific stock analysis
specific_stock_analysis = run_specific_stock_analysis(
    subreddits, "TSLA", limit=10, stock_data_period="1mo"
)

# print the results
print("Top Stock:", top_stock)
print("Worst Stock:", worst_stock)
print("Rising Stock:", rising_stock)
print("Specific Stock Analysis:", specific_stock_analysis)