from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from os import environ

import requests
from invokes import invoke_http

import pika
import amqp_setup
import json

app = Flask(__name__)
CORS(app)

<<<<<<< Updated upstream
portfolioURL = environ.get('portfolio_URL') or "http://127.0.0.1:5001/portfolio"
fundsURL = environ.get('funds_URL') or "http://127.0.0.1:5002/funds"
profileURL = environ.get('profile_URL') or "http://127.0.0.1:5003/profile"

@app.route("/userprofile/<string:user_id>")
def userprofile(user_id):
 
    try:
        # information = request.get_json()
        print("\nReceived information:", user_id)
        # print(type(information))
        result = processPortfolio(user_id)
=======
portfolioURL = "http://127.0.0.1:5001/portfolio"
fundsURL = "http://127.0.0.1:5002/funds"
profileURL = "http://127.0.0.1:5003/profile"
yahooURL = "http://127.0.0.1:5900/stock"
errorURL = "http://127.0.0.1:5005/error"


@app.route("/userprofile", methods=["POST"])
def userprofile():
    # Simple check of input format and data of the request are JSON

    if request.is_json:
        try:
            userid = request.get_json()
            print("\nReceived information in JSON:", userid)
    
            user_stocks = processStocks(userid) # returns information of stocks under user
            user_information = processPortfolio(userid) # returns information of user
>>>>>>> Stashed changes

        if result['code'] in range(200,300):
            return jsonify({
                "code": 200,
                "user_stocks": user_stocks,
                "user_information": user_information
            }),200 
        else: 
            return jsonify(result), 500

    except Exception as e:
                    # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + \
            fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "userprofile.py internal error: " + ex_str
        }), 500


def processStocks(userid):
    
    name = userid['user_id'] 

    print('\-----Invoking Portfolio microservice----') # calls portfolio microservice to get the stocks under the user
    personal_stocks_result = invoke_http(portfolioURL + "/" + name, method="GET")
    print('personal stocks result', personal_stocks_result)
    
    stocks = personal_stocks_result['stocks']
    stock_list = []
    for stock in stocks:
        stockid = stock['stock_id']
        stock_results = invoke_http(yahooURL + "/" + stockid, method="GET")
        stock_list.append(stock_results)
    
    return {
        "code": 201,
        "data": {
            "stock_results": stock_list
        }
    }
    

def processPortfolio(userid):
    print('\n----Invoking profile microservice----')

    profile_result = invoke_http(profileURL + "/" + userid, method="GET")
    print(profile_result)
    print(type(profile_result))
    code = profile_result['code']
    # Sending error to error.py if there are issues with retriving profile information 
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                            body=profile_result['message'], properties=pika.BasicProperties(delivery_mode=2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), profile_result)

        return profile_result
    print('profile result: ', profile_result)

    print('\n----Invoking portfolio microservice----')
    portfolio_result = invoke_http(portfolioURL + "/" + userid, method="GET")

    # Sending error to error.py if there are issues with retriving portfolio information, below 500 as it will return 404 if there are no portfolio
    if portfolio_result['code'] not in range(200, 500):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                            body=portfolio_result['message'], properties=pika.BasicProperties(delivery_mode=2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), portfolio_result)

        return portfolio_result
    print('portfolio result: ', portfolio_result)

    print('\n----Invoking funds microservice----')
<<<<<<< Updated upstream
    funds_result = invoke_http(fundsURL + "/" + userid, method="GET")
    # Sending error to error.py if there are issues with retriving funds information 
    if funds_result['code'] not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                            body=funds_result['message'], properties=pika.BasicProperties(delivery_mode=2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), funds_result)

        return funds_result
    print('funds result: ', funds_result)
=======
    funds_result = invoke_http(fundsURL + "/" + name, method="GET")
    print('funds result: ', funds_result)    
>>>>>>> Stashed changes

    return {
        "code": 201,
        "data": {
            "profile_result": profile_result,
            "portfolio_result": portfolio_result,
            "funds_result": funds_result
        }
    }
    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for retrieving customer's information...")
    app.run(host="0.0.0.0", port=5008, debug=True)
        