from main import app
import os

# Print environment check for debugging purposes
if __name__ == "__main__":
    print("Environment variables check:")
    print(f"REDDIT_CLIENT_ID present: {'Yes' if os.getenv('REDDIT_CLIENT_ID') else 'No'}")
    print(f"REDDIT_CLIENT_SECRET present: {'Yes' if os.getenv('REDDIT_CLIENT_SECRET') else 'No'}")
    print(f"REDDIT_USER_AGENT present: {'Yes' if os.getenv('REDDIT_USER_AGENT') else 'No'}")
    
    app.run()
