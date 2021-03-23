##############################################
# Microservice to call all Yahoo Finance API #
##############################################


from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import json 
import yfinance as yf

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)


# Keys to call Yahoo Finance API
headers = {
    'x-rapidapi-key': "b09591b193mshad22b0d68b19f4ap167b63jsnceb43796bf13",
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }


# To get the top 10 gainers and losers of the day
@app.route("/market")
def market_summary():

    print("------ Getting stock symbols for top 10 gainers and losers -----")

    try: 
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-movers"

        querystring = {"region":"SG","lang":"en-US","start":"0","count":"10"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        result = json.loads(response.text)

        return jsonify(
            {
                "code": 200,
                "results": {
                    "gainers": result["finance"]["result"][0]["quotes"],
                    "losers": result["finance"]["result"][1]["quotes"]
                }
            }
        )

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + \
            fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "Error getting top 10 gainers and loser: " + ex_str
        }), 500


# To get information on the stock 
@app.route("/stock/<string:stock_id>")
def stock_info(stock_id):


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900, debug=True)