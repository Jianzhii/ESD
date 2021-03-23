#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys

import requests
from invokes import invoke_http

import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)


############# URLS to other microservices ####################
funds_url = "http://localhost:5002/funds/"
portfolio_url = "http://localhost:5001/portfolio"
#profile_url = "http://localhost:5003/profile"
yahoo_friends_url = ""
##############################################################


@app.route("/order/buy", methods=['PUT'])
def buy_stocks():

    print('-----Starting Buying Microservice-----')

    # Check if buy order inputs are in proper json format
    if request.is_json:
        try:
            buy_order = request.get_json()
            pricePerStock = getPrice(buy_order["stock_id"])
            qty = buy_order["quantity"]
            customer_id = buy_order["customer_id"]
            stock_id = buy_order["stock_id"]
            amount = pricePerStock * qty
            customer_id = buy_order["customer_id"]

            # check yahoo friends??

            result = processBuy(customer_id, stock_id,
                                pricePerStock, qty, amount)

            if result != True:
                return result
            else:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Buy success",
                        "details": {
                            "customer_id": customer_id,
                            "stock_id": stock_id,
                            "pricePerStock": pricePerStock,
                            "quantity": qty,
                            "amount": amount
                        }
                    }
                ), 200
                # update user portfolio
                

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + \
                fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "order_management.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processBuy(customer_id, stock_id, pricePerStock, qty, amount):

    print('\n-----Invoking funds microservice-----')
    print(customer_id, amount)

    json = {
        "action": "SPEND",
        "amount": amount
    }

    # Checking funds availability 
    avail = invoke_http(funds_url + customer_id, method="PUT", json=json)

    if avail['code'] not in range(200, 300):
        return avail
    else:
        print('\n-----Invoking portfolio microservice-----')
        json = {
            "customer_id": customer_id,
            "stock_id": stock_id,
            "price": pricePerStock,
            "quantity": qty
        }

        # Updating portfolio on purchase
        avail = invoke_http(portfolio_url, method="POST", json=json)
        if avail['code'] not in range(200, 300):
            return avail
        else:
            return True


def getPrice(stock_id):
    return 20.00


@app.route('/order/sell', methods=['PUT'])
def sell_stocks():

    print('-----Starting Selling Microservice-----')

    # Check if buy order inputs are in proper json format
    if request.is_json:
        try:
            sell_order = request.get_json()
            pricePerStock = getPrice(sell_order["stock_id"])
            qty = sell_order["quantity"]
            customer_id = sell_order["customer_id"]
            stock_id = sell_order["stock_id"]
            amount = pricePerStock * qty
            customer_id = sell_order["customer_id"]

            # check yahoo friends??

            result = processSell(customer_id, stock_id, qty, amount)

            if result["code"] not in range(200, 300):
                return result
            else:
                cost = 0
                for stock in result["data"]:
                    cost += stock["price"] * stock["quantity"]
                
                profit = amount - cost

                return jsonify(
                    {
                        "code": 201,
                        "message": "Sell success",
                        "details": {
                            "customer_id": customer_id,
                            "stock_id": stock_id,
                            "profit" : profit,
                            "priceperstock" : pricePerStock
                        },
                        "prices": result["data"]
                    }
                ), 201
                # update user portfolio

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + \
                fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "order_management.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processSell(customer_id, stock_id, qty, amount):
    print('\n-----Invoking portfolio microservice-----')

    json = {
        "customer_id": customer_id,
        "stock_id": stock_id,
        "quantity": qty
    }

    # Checking on stocks availability in portfolio and update accordingly
    stocks = invoke_http(portfolio_url, method="PUT", json=json)

    if stocks['code'] not in range(200, 300):
        return stocks
    else:
        print('\n-----Invoking funds microservice-----')
        json = {
            "action": "LOAD",
            "amount": amount
        }

        # Updating funds after successful sales
        invoke_http(funds_url + customer_id, method="PUT", json=json)
        return stocks

def getPrice(stock_id):
    return 30.00

# Function to update user portfolio after successful purchase of stocks
# Order type will be buy or sell. Buying only involves update after successful purchase. Selling involves checking and updating only if sell is possible
def update_portfolio(order, order_type):
    pass

# Function to call Yahoo's Friend??

def yahoo_friend():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
