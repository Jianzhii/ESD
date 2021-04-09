#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://root@localhost:3306/funds'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)


class Fund(db.Model):
    __tablename__ = 'funds'

    user_id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float(precision=2), nullable=False)
    spent = db.Column(db.Float(precision=2), nullable=False)

    def json(self):
        return {
            'user_id': self.user_id,
            'balance': self.balance,
            'spent': self.spent
        }


@app.route("/funds")
def get_all():
    funds = Fund.query.all()
    if len(funds):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "funds": [fund.json() for fund in funds]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no entries."
        }
    ), 404


@app.route("/funds/<int:user_id>")
def find_by_user_id(user_id):
    funds = Fund.query.filter_by(user_id=user_id).first()
    if funds:
        return jsonify(
            {
                "code": 200,
                "fund": funds.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "user_id": user_id
            },
            "message": "No funds found."
        }
    ), 404


@app.route("/funds/<int:user_id>", methods=['POST'])
def create_fund(user_id):
    portfolio = Fund.query.filter_by(
        user_id=user_id).first()
    if portfolio:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "user_id": user_id
                },
                "message": "User already exists."
            }
        ), 404

    # update status
    data = request.get_json()
    fund = Fund(user_id=user_id, spent=0.00, **data)
    try:
        db.session.add(fund)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the fund. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": fund.json()
        }
    ), 201


@app.route("/funds/<int:user_id>", methods=['PUT'])
def update_order(user_id):
    try:
        fund = Fund.query.filter_by(
            user_id=user_id).first()
        print(fund)
        if not fund:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "user_id": user_id
                    },
                    "message": "Customer not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['action'] == "LOAD":
            fund.balance += data['amount']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": "Funds added",
                    "data": fund.json()
                }
            ), 200
        elif data['action'] == "SPEND":
            bal = fund.balance
            if bal < float(data['amount']):
                return jsonify(
                    {
                        "code": 501,
                        "data": {
                            "user_id": user_id,
                            "balance": bal
                        },
                        "message": "Not enough available funds. Please top-up."
                    }
                ), 501
            else:
                fund.balance -= data['amount']
                fund.spent += data['amount']
                db.session.commit()
                return jsonify(
                    {
                        "code": 201,
                        "message": "Funds deducted",
                        "data": fund.json()
                    }
                ), 201

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "user_id": user_id,
                },
                "message": "An error occurred while updating the funds. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) +
          ": manage funds ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
