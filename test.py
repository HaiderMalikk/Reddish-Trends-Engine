from market_sentiment_analysis import run_general_analysis, run_specific_stock_analysis
from data_processing import get_top_stock, get_worst_stock, get_rising_stock
from gpt_processing import analyze_stock_data_with_gpt

# Define the subreddits to analyze
subreddits = ["wallstreetbets", "stocks", "stockmarket"]

# gebeneral stock analysis'
# run the specific stock analysis
gen = run_general_analysis(subreddits, 10, 10, "hot", "1mo")
specific_stock_analysis = run_specific_stock_analysis(subreddits, ["$GOGO", "$ASAN"], 10, 10, "hot", "1mo")
get_top_stock(gen)
get_worst_stock(gen)
get_rising_stock(gen)
analyze_stock_data_with_gpt(gen)

# print the results
print("specific_stock_analysis:", specific_stock_analysis)
print("general_stock_analysis:", gen)
print("top_stock:", get_top_stock(gen))
print("worst_stock:", get_worst_stock(gen))
print("rising_stock:", get_rising_stock(gen))
print("gpt_analysis:", analyze_stock_data_with_gpt(gen))
