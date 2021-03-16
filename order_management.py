#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request, jsonify

from invokes import invoke_http

app = Flask(__name__)

@app.route("/order/buy")
def buy_stocks():

    print('-----Starting Microservice-----')

    ## Check if user has sufficient funds
    # HTTP request to user funds to get boolean 

def funds_check(userID, cost):

    print('-----Checking User Fund Balance-----')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)