#############################################################
# Microservice to manage all buy/sell orders from customers #
#############################################################

from flask import Flask, request, session, redirect
from flask_cors import CORS
from invokes import invoke_http

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = "SrocErkkgz0zd15PykMxuSUwtzidl2Yd"

CORS(app)

############# URLS to other microservices ####################
funds_url = "http://localhost:5002/funds/"
portfolio_url = "http://localhost:5001/portfolio"
profile_url = "http://localhost:5003/profile/"
yahoo_friends_url = ""
##############################################################

CLIENT_ID = "954992833627-gdo27oikggjmrrqhc6ai2hq8ncmcrvjm.apps.googleusercontent.com"


@app.route("/auth", methods=['POST'])
def auth():
    print('-----Starting Auth Microservice-----')
    token = request.get_data().decode('utf-8')

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)
        userid = idinfo['sub']
        name = idinfo['name']
        email = idinfo['email']
        session['userID'] = userid
        check(userid, name, email)
        return redirect('home.html', code=302)

    except ValueError:
        # Invalid token
        return "invalid token"


def check(userid, name, email):
    # Checking if user exists
    print('\n-----Invoking profile microservice-----')
    print(userid)
    json = {
        "name": name,
        "email": email
    }
    avail = invoke_http(profile_url + userid, method="POST", json=json)
    print(avail)
    if avail['code'] == 404:
        pass
    elif avail['code'] not in range(200, 300):
        return avail
    else:
        print('\n-----Invoking funds microservice-----')
        json = {
            "balance": 500
        }

        # Updating portfolio on purchase
        avail = invoke_http(funds_url + userid, method="POST", json=json)
        if avail['code'] not in range(200, 300):
            return avail
        else:
            return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)