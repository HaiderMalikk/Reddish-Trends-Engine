# simple flask test app
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    
    return "Hello World!"

if __name__ == "__main__":
    app.run()
    
# Run the app
# python3 main.py