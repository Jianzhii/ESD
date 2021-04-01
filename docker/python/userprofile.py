from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import json

app = Flask(__name__)
CORS(app)

portfolioURL = "http://127.0.0.1:5001/portfolio"
fundsURL = "http://127.0.0.1:5002/funds"
profileURL = "http://127.0.0.1:5003/profile"
errorURL = "http://127.0.0.1:5005/error"

@app.route("/userprofile")
def userprofile():
    # Simple check of input format and data of the request are JSON

    if request.is_json:
        try:
            information = request.get_json()
            print("\nReceived information in JSON:", information)
            # print(type(information))
            result = processPortfolio(information)

            return jsonify({
                "code": 200,
                "results": result
            }),200 

        except Exception as e:
            pass
        
    else:        
        return jsonify({
                "code": 400,
                "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

def processPortfolio(userid):
    print('\n----Invoking profile microservice----')

    # retrieve value from user_id key
    name = userid["user_id"]

    profile_result = invoke_http(profileURL + "/" + name, method="GET")
    print('profile result: ', profile_result)

    print('\n----Invoking portfolio microservice----')
    portfolio_result = invoke_http(portfolioURL + "/" + name, method="GET")
    print('portfolio result: ', portfolio_result)

    print('\n----Invoking funds microservice----')
    funds_result = invoke_http(fundsURL + "/" + name, method="GET")
    print('funds result: ', funds_result)

    

    return {
        "code": 201,
        "data": {
            "profile_result": profile_result,
            "portfolio_result": portfolio_result,
            "funds_result": funds_result
        }
    }
    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5008, debug=True)
        