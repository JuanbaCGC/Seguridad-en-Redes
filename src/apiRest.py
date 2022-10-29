#!/usr/bin/env python3

from flask import Flask
from flask import jsonify, request
from flask_restful import Resource, Api
import secrets

from users import usersList

app = Flask(__name__)
api = Api(app)


@app.route('/version', methods=['GET'])
def getVersion():
    return jsonify({"Version":"1.0"})

@app.route('/signup', methods=['POST'])
def signup():
    newUser = {
        "name": request.json['name'],
        "password": request.json['password']
    }
    userFound = [users for users in usersList if users['name'] == request.json['name']]
    if (len(userFound) > 0):
        return jsonify({"ErrorMessage": "There is a user with the same name. Try other user name."})
    usersList.append(newUser)
    token = secrets.token_urlsafe(20)
    return jsonify({"Message": "User Added Succesfully", "User token": token})


if __name__ == '__main__':
    app.run(debug=True)