#!/usr/bin/env python3

from flask import Flask
from flask import jsonify, request
from flask_restful import Resource, Api

from users import users

app = Flask(__name__)
api = Api(app)


@app.route('/version', methods=['GET'])
def getVersion():
    return jsonify({"version":"1.0"})

@app.route('/signup', methods=['POST'])
def signup():
    newUser = {
        "name": request.json['name'],
        "password": request.json['password']
    }
    users.append(newUser)
    return jsonify({"message": "User Added Succesfully", "users": users})


if __name__ == '__main__':
    app.run(debug=True)