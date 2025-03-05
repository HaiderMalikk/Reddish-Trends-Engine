# simple flask test app
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("Flask Server Running")

@app.route("/api/home", methods=["GET", "POST"])
def get_analysis():
    response_data = {}

    if request.method == "POST":
        data = request.get_json()
        
        response_data["Message"] = "Data Received returning data"
        response_data["Data you sent"] = data
        
    elif request.method == 'GET':
        print("GET request received. Returning default response.")
        response_data = {
            'message': 'This endpoint supports POST requests for processing data.',
        }
    
    print("Response Data:", response_data)
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, port=8080) # TODO turn of debug

# Run the app
# python3 main.py
