#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request, jsonify

from invokes import invoke_http

app = Flask(__name__)



############# URLS to other microservices ####################
user_fund_url = '' 
user_portfolio_url = ''
yahoo_friends_url = ''
##############################################################


@app.route("/order/buy")
def buy_stocks():

    print('-----Starting Buying Microservice-----')

    # Check if buy order inputs are in proper json formar
    if request.is_json():
        try: 
            buy_order = request.get_json() 

            if funds_check(buy_order):

                # check yahoo friends??

                # update user portfolio 

            ## Check if user has sufficient funds
            # HTTP request to user funds to get boolean 

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
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


@app.route('/order/sell')
def sell_stocks():

    print('-----Starting Selling Microservice-----')

    # Check if input is in proper json format
    if request.is_json():

        try: 

        except Exception as e:  

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400



# Function to check user fund balance when user is buying stocks
def funds_check(buy_order):

    print('-----Checking User Fund Balance-----')
    fund_balance = invoke_http(user_fund_url, method='GET', json=buy_order)

    # depending on Asher's code in User Funds and return results 


# Function to update user portfolio after successful purchase of stocks
# Order type will be buy or sell. Buying only involves update after successful purchase. Selling involves checking and updating only if sell is possible
def update_portfolio(order, order_type):


# Function to call Yahoo's Friend??
def yahoo_friend():


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)