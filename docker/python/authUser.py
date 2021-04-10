#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request,jsonify
from flask_cors import CORS, cross_origin
import os
import sys
from os import environ
from invokes import invoke_http

from google.oauth2 import id_token
from google.auth.transport import requests

import pika
import amqp_setup
import json

app = Flask(__name__)
app.secret_key = "SrocErkkgz0zd15PykMxuSUwtzidl2Yd"

CORS(app, support_credentials=True)

############# URLS to other microservices ####################
#portfolio_url = environ.get('portfolio_URL') or "http://localhost:5001/portfolio"
funds_url = environ.get('funds_URL') or "http://localhost:5002/funds"
profile_url = environ.get('profile_URL') or "http://localhost:5003/profile"
yahoo_friends_url = ""
##############################################################

CLIENT_ID = "954992833627-gdo27oikggjmrrqhc6ai2hq8ncmcrvjm.apps.googleusercontent.com"


@app.route("/auth", methods=['POST'])
@cross_origin(supports_credentials=True)
def auth():
    print('-----Starting Auth Microservice-----')
    token = request.get_data().decode('utf-8')

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)
        userid = idinfo['sub']
        print(userid)
        name = idinfo['name']
        email = idinfo['email']
        check(userid, name, email)
        return jsonify({'userid': userid, 'name': name}),200

    except ValueError:
        # Invalid token
        return "invalid token"


def check(userid, name, email):
    # Checking if user exists
    print('\n-----Invoking profile microservice-----')
    print(userid)
    user_info = {
        "name": name,
        "email": email
    }
    avail = invoke_http(profile_url + "/" + userid, method="POST", json=user_info)
    code = avail['code']
    print(code)

    message = json.dumps(avail)

    if code == 201:
        print('\n-----Invoking funds microservice-----')
        fund_info = {
            "balance": 500
        }

        #create fund for new user
        avail = invoke_http(funds_url + "/" + userid, method="POST", json=fund_info)
        message = json.dumps(avail)

        if avail['code'] not in range(200, 300):

            # Inform the error microservice
            #print('\n\n-----Invoking error microservice as order fails-----')
            print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                            body=message, properties=pika.BasicProperties(delivery_mode=2))

            print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
                code), avail)

            return avail
        else:
            return userid
    
    elif code == 403:
        #customer already exists
        return userid
    else:

        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))

        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), avail)

        return avail
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
