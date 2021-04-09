#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request, jsonify
from flask.signals import signals_available
from flask_cors import CORS

import os
import sys
from os import environ

import requests
from invokes import invoke_http

import pika
import amqp_setup
import json

app = Flask(__name__)
CORS(app)


############# URLS to other microservices ####################
portfolio_url = environ.get(
    'portfolio_URL') or "http://localhost:5001/portfolio"
funds_url = environ.get('funds_URL') or "http://localhost:5002/funds"
##############################################################


@app.route("/order/buy", methods=['PUT'])
def buy_stocks():

    print('-----Starting Buying Microservice-----')

    # Check if buy order inputs are in proper json format
    if request.is_json:
        try:
            buy_order = request.get_json()
            pricePerStock = buy_order["price"]
            qty = buy_order["quantity"]
            user_id = buy_order["user_id"]
            stock_id = buy_order["stock_id"]
            amount = float(pricePerStock) * float(qty)
            
            print(user_id, stock_id, pricePerStock, qty, amount)

            result = processBuy(user_id, stock_id, pricePerStock, qty, amount)

            if result != True:
                return jsonify(result), 501
            else:
                return jsonify(
                    {
                        "code": 200,
                        "message": "Buy success",
                        "details": {
                            "user_id": user_id,
                            "stock_id": stock_id,
                            "pricePerStock": pricePerStock,
                            "quantity": qty,
                            "amount": amount
                        }
                    }
                ), 200  

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


def processBuy(user_id, stock_id, pricePerStock, qty, amount):

    print('\n-----Invoking funds microservice-----')
    print(user_id, amount)

    buy_data = {
        "action": "SPEND",
        "amount": amount
    }

    # Checking funds availability
    funds_result = invoke_http(funds_url + "/" + user_id, method="PUT", json=buy_data)
    code = funds_result["code"]
    message = json.dumps(funds_result)
   

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))

        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), funds_result)

        return funds_result
    else:

        # 4. Record new order
        # record the activity log anyway
        # print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (order info) message with routing_key=order.info-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
                                         body=message)

        print("\nOrder published to RabbitMQ Exchange.\n")
        # - reply from the invocation is not used;
        # continue even if this invocation fails

        print('\n-----Invoking portfolio microservice-----')
        portfolio_data = {
            "user_id": user_id,
            "stock_id": stock_id,
            "quantity": qty,
            "price": pricePerStock
        }

        # Updating portfolio on purchase
        portfolio_result = invoke_http(portfolio_url, method="POST", json=portfolio_data)
        message = json.dumps(portfolio_result)
        if portfolio_result['code'] not in range(200, 300):
            return portfolio_result
        else:

            print( '\n\n-----Publishing the (order info) message with routing_key=order.info-----')

            # invoke_http(activity_log_URL, method="POST", json=order_result)
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
                                            body=message)

            print("\nOrder published to RabbitMQ Exchange.\n")

            return True

@app.route('/order/sell', methods=['PUT'])
def sell_stocks():

    print('-----Starting Selling Microservice-----')

    # Check if buy order inputs are in proper json format
    if request.is_json:
        try:
            sell_order = request.get_json()
            pricePerStock = sell_order["price"]
            qty = sell_order["quantity"]
            user_id = sell_order["user_id"]
            stock_id = sell_order["stock_id"]
            amount = float(pricePerStock) * float(qty)
            
            result = processSell(user_id, stock_id, qty, amount)

            if result["code"] not in range(200, 300):
                return jsonify(result),501

            else:
                cost = 0
                for stock in result["data"]:
                    cost += float(stock["price"]) * float(stock["quantity"])
                    
                profit = amount - cost

                return jsonify(
                    {
                        "code": 201,
                        "message": "Sell success",
                        "details": {
                            "user_id": user_id,
                            "stock_id": stock_id,
                            "profit": profit,
                            "priceperstock": pricePerStock
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


def processSell(user_id, stock_id, qty, amount):
    print('\n-----Invoking portfolio microservice-----')

    sales = {
        "user_id": user_id,
        "stock_id": stock_id,
        "quantity": qty
    }

    # Checking on stocks availability in portfolio and update accordingly
    portfolio_results = invoke_http(portfolio_url, method="PUT", json=sales)
    code = portfolio_results["code"]
    message = json.dumps(portfolio_results)

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), portfolio_results)

        return portfolio_results
    else:
         # 4. Record new order
        # record the activity log anyway
        # print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (order info) message with routing_key=order.info-----')

        # invoke_http(activity_log_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
                                         body=message)

        print("\nOrder published to RabbitMQ Exchange.\n")
        # - reply from the invocation is not used;
        # continue even if this invocation fails

        print('\n-----Invoking funds microservice-----')
        funds_top_up = {
            "action": "LOAD",
            "amount": amount
        }

        # Updating funds after successful sales
        funds_results = invoke_http(funds_url + "/" + user_id, method="PUT", json=funds_top_up)
        message = json.dumps(funds_results)
        print( '\n\n-----Publishing the (order info) message with routing_key=order.info-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
                                         body=message)

        print("\nOrder published to RabbitMQ Exchange.\n")
        
        return portfolio_results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
