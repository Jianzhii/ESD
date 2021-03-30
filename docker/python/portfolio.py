#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://root@localhost:3306/portfolio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)


class Portfolio(db.Model):
    __tablename__ = 'portfolio'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    stock_id = db.Column(db.String(32), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'price': self.price,
            'quantity': self.quantity
        }


@app.route("/portfolio")
def get_all():
    PortfolioList = Portfolio.query.all()
    if len(PortfolioList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [stock.json() for stock in PortfolioList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no entries."
        }
    ), 404


@app.route("/portfolio/<string:user_id>")
def find_by_user_id(user_id):
    portfolio = Portfolio.query.filter_by(user_id=user_id)
    if portfolio:
        return jsonify(
            {
                "code": 200,
                "stocks": [stock.json() for stock in portfolio]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "user_id": user_id
            },
            "message": "No portfolio found."
        }
    ), 404


@app.route("/portfolio/<string:user_id>/<string:stock_id>")
def find_by_portfolio_id(user_id, stock_id):
    portfolio = Portfolio.query.filter_by(
        user_id=user_id).filter_by(stock_id=stock_id)

    if portfolio:
        return jsonify(
            {
                "code": 200,
                "stocks": [stock.json() for stock in portfolio]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "user_id": user_id
            },
            "message": "No portfolio found."
        }
    ), 404


@app.route("/portfolio", methods=['POST'])
def create_order():
    data = request.get_json()
    print(data)
    portfolio = Portfolio(**data)
    # convert a JSON object to a string and print
    print(json.dumps(portfolio.json(), default=str))
    print()
    try:
        db.session.add(portfolio)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500
    # convert a JSON object to a string and print
    print(json.dumps(portfolio.json(), default=str))
    print()
    return jsonify(
        {
            "code": 201,
            "data": portfolio.json()
        }
    ), 201


@app.route("/portfolio", methods=['PUT'])
def update_order():
    user_id = request.json.get('user_id', None)
    stock_id = request.json.get('stock_id', None)

    try:
        portfolio = Portfolio.query.filter_by(
            user_id=user_id).filter_by(stock_id=stock_id)
        if not portfolio:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "stock_id": stock_id
                    },
                    "message": "Stock not found."
                }
            ), 404

        # update status
        total = 0
        for stock in portfolio:
            total += stock.json()["quantity"]

        quantity = request.json.get('quantity', None)
        if int(quantity) > total:
            return jsonify(
                {
                    "code": 501,
                    "data": {
                        "user_id": user_id,
                        "stock_id": stock_id,
                        "balance": total
                    },
                    "message": "Can't sell more than available stock."
                }
            ), 501

        else:
            sold = []
            for stock in portfolio:
                qty = stock.json()["quantity"]
                if int(quantity) >= qty:
                    quantity = int(quantity)
                    quantity -= qty
                    sold.append(
                        {"quantity": qty, "price": stock.json()["price"]})
                    try:
                        db.session.delete(stock)
                        db.session.commit()
                    except:
                        return jsonify(
                            {
                                "code": 500,
                                "data": {
                                    "stock_id": stock_id
                                },
                                "message": "An error occurred deleting the stock."
                            }
                        ), 500
                else:
                    sold.append(
                        {"quantity": quantity, "price": stock.json()["price"]})
                    try:
                        stock.quantity -= int(quantity)
                        db.session.commit()
                    except:
                        return jsonify(
                            {
                                "code": 501,
                                "data": {
                                    "stock_id": stock_id
                                },
                                "message": "An error occurred editing the stock."
                            }
                        ), 501
                    print(sold)
                    return jsonify(
                        {
                            "code": 200,
                            "data": sold
                        }
                    ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "user_id": user_id,
                    "stock_id": stock_id

                },
                "message": "An error occurred while updating the stock quantity. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) +
          ": manage portfolio ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
