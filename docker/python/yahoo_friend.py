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
    'x-rapidapi-key': "c76e11c753msha38f73a10c16b1dp1443c3jsndf66c4b08501",
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }


# second api key:  b09591b193mshad22b0d68b19f4ap167b63jsnceb43796bf13


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

    print(f"----- Getting {stock_id} information -----")

    try: 
        stock = yf.Ticker(stock_id)
        stock_info = stock.info
        
        one_day = stock.history(period='1d')
        one_week = stock.history(period='1wk')
        one_month = stock.history(period='1mo')
        six_month = stock.history(period='6mo')
        
        result = {
                "code": 200,
                "results": {
                    "name": stock_info['longName'],
                    "previousClose": stock_info['previousClose'],
                    "open": stock_info['open'],
                    "volume": stock_info['volume'],
                    "averageVolume": stock_info['averageVolume'],
                    "ask": stock_info['ask'],
                    "askSize": stock_info['askSize'],
                    "bid": stock_info['bid'],
                    "bidSize": stock_info['bidSize'],
                    "marketCap": stock_info['marketCap'],
                    "historical_data": {
                        "one_day": {
                            "date": one_day.index.values.tolist(),
                            "price": one_day['Close'].tolist()
                        },
                        "one_week": {
                            "date": one_week.index.values.tolist(),
                            "price": one_week['Close'].tolist()
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

        return jsonify(result)

    except (ValueError, KeyError, NameError):
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-statistics"

        querystring = {"symbol": stock_id}

        response = requests.request("GET", url, headers=headers, params=querystring)

        result = json.loads(response.text)

        price_url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data"

        price_querystring = {"symbol":stock_id}

        price_response = requests.request("GET", price_url, headers=headers, params=price_querystring)

        price_result = json.loads(price_response.text)

        output = {
                "code": 200,
                "results": {
                    "name": result['price']['longName'],
                    "historical_data": {
                        "one_day": {
                            "date": [price_result['prices'][i]['date'] for i in range(min(2, len(price_result['prices'])))][::-1],
                            "price": [price_result['prices'][i]['close'] for i in range(min(2, len(price_result['prices'])))][::-1]
                        },
                        "one_week": {
                            "date": [price_result['prices'][i]['date'] for i in range(min(5,len(price_result['prices'])))][::-1],
                            "price": [price_result['prices'][i]['close'] for i in range(min(5,len(price_result['prices'])))][::-1]
                        },
                        "one_month": {
                            "date": [price_result['prices'][i]['date'] for i in range(min(20,len(price_result['prices'])))][::-1],
                            "price": [price_result['prices'][i]['close'] for i in range(min(20,len(price_result['prices'])))][::-1]
                        },
                        "six_month": {
                            "date": [price_result['prices'][i]['date'] for i in range(min(125,len(price_result['prices'])))][::-1],
                            "price": [price_result['prices'][i]['close'] for i in range(min(125,len(price_result['prices'])))][::-1]
                        }
                    }
                }
        }
        
        values = ['previousClose','open', 'volume','averageVolume','ask','askSize','bid','bidSize']

        for each in values:
            if len(result['summaryDetail'][each]) == 0:
                output['results'][each] = "N/A"
            else:
                output['results'][each] = result['summaryDetail'][each]['raw']

        if len(result['price']['marketCap']) == 0:
            output['results']['marketCap'] = "N/A"
        else:
            output['results']['marketCap'] = result['price']['marketCap']['raw']

        return jsonify(output)


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