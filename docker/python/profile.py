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
    'dbURL') or 'mysql+mysqlconnector://root@localhost:3306/profile'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)


class Profile(db.Model):
    __tablename__ = 'profile'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)

    def json(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email
        }


@app.route("/profile")
def get_all():
    profiles = Profile.query.all()
    if len(profiles):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "profiles": [profile.json() for profile in profiles]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no entries."
        }
    ), 404


@app.route("/profile/<string:user_id>")
def find_by_user_id(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return jsonify(
            {
                "code": 200,
                "profile": profile.json()
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


@app.route("/profile/<int:user_id>", methods=['POST'])
def create_fund(user_id):
    portfolio = Profile.query.filter_by(
        user_id=user_id).first()

    if portfolio:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "user_id": user_id
                },
                "message": "Customer already exists."
            }
        ), 404

    # update status
    data = request.get_json()
    print(data)
    name = data["name"]
    email = data["email"]
    profile = Profile(user_id=user_id, name=name, email=email)
    try:
        db.session.add(profile)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the profile. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": profile.json()
        }
    ), 201


@app.route("/profile/<int:user_id>", methods=['PUT'])
def update_order(user_id):

    profile = Profile.query.filter_by(
        user_id=user_id).first()
    if profile:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "user_id": user_id
                },
                "message": "User already exists."
            }
        ), 404

    try:
        # update status
        data = request.get_json()
        name = data["name"]
        email = data["email"]
        profile = Profile(user_id=user_id, name=name, email=email)
        db.session.commit()

        return jsonify(
            {
                "code": 201,
                "data": profile.json()
            }
        ), 201

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "user_id": user_id,
                },
                "message": "An error occurred while updating the user profile. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) +
          ": manage profile ...")
    app.run(host='0.0.0.0', port=5003, debug=True)
