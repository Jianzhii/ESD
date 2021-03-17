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
    customer_id = db.Column(db.Integer, nullable=False)
    stock_id = db.Column(db.String(32), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
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


@app.route("/portfolio/<string:customer_id>")
def find_by_customer_id(customer_id):
    portfolio = Portfolio.query.filter_by(customer_id=customer_id)
    if portfolio:
        return jsonify(
            {
                "code": 200,
                "stocks": [portfolio.json() for portfolio in portfolio]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "customer_id": customer_id
            },
            "message": "No portfolio found."
        }
    ), 404


@app.route("/portfolio/<string:customer_id>/<string:stock_id>")
def find_by_portfolio_id(customer_id, stock_id):
    portfolio = Portfolio.query.filter_by(
        customer_id=customer_id).filter_by(stock_id=stock_id)

    if portfolio:
        return jsonify(
            {
                "code": 200,
                "stocks": [portfolio.json() for portfolio in portfolio]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "customer_id": customer_id
            },
            "message": "No portfolio found."
        }
    ), 404


@app.route("/portfolio/<string:customer_id>", methods=['POST'])
def add_portfolio(customer_id):
    data = request.get_json()
    stock = Portfolio(customer_id=customer_id, **data)

    try:
        db.session.add(stock)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while adding the portfolio. " + str(e)
            }
        ), 500

    # convert a JSON object to a string and print
    print(json.dumps(stock.json(), default=str))
    print()

    return jsonify(
        {
            "code": 201,
            "data": stock.json()
        }
    ), 201


@app.route("/portfolio/<string:customer_id>/<string:stock_id>", methods=['PUT'])
def update_order(customer_id,stock_id):
    try:
        portfolio = Portfolio.query.filter_by(
            customer_id=customer_id).filter_by(stock_id=stock_id).first()
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
        data = request.get_json()
        if data['action'] == "BUY":
            portfolio.quantity += data['quantity']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": portfolio.json()
                }
            ), 200
        elif data['action'] == "SELL":
            portfolio.quantity -= data['quantity']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": portfolio.json()
                }
            ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "customer_id":customer_id,
                    "stock_id":stock_id

                },
                "message": "An error occurred while updating the stock quantity. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) +
          ": manage portfolio ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
