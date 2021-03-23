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
            "message": "Error getting top 10 gainers and loser with the following error: \n" + ex_str
        }), 500


# To get information on the stock 
@app.route("/stock/<string:stock_id>")
def stock_info(stock_id):

    print("----- Getting individual stock information -----")

    try: 
        stock = yf.Ticker(stock_id)
        stock_info = stock.info

        one_day = stock.history(period='1d')
        one_month = stock.history(period='1mo')
        six_month = stock.history(period='6mo')
        
        return jsonify(
            {
                "code": 200,
                "results": {
                    "name": stock_info['longName'],
                    "previousClose": stock_info['previousClose'],
                    "open": stock_info['open'],
                    "volume": stock_info['volume'],
                    "averageVolume": stock_info['averageVolume'],
                    "sell_price": stock_info['ask'],
                    "sell_qty": stock_info['askSize'],
                    "buy_price": stock_info['bid'],
                    "buy_qty": stock_info['bidSize'],
                    "marketCap": stock_info['marketCap'],
                    "historical_data": {
                        "one_day": {
                            "date": one_day.index.values.tolist(),
                            "price": one_day['Close'].tolist()
                        },
                        "one_month": {
                            "date": one_month.index.values.tolist(),
                            "price": one_month['Close'].tolist()
                        },
                        "six_month": {
                            "date": six_month.index.values.tolist(),
                            "price": six_month['Close'].tolist()
                        }
                    }
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
            "message": "Error getting stock information with the following error: \n" + ex_str
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900, debug=True)