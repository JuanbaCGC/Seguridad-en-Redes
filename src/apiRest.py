#!/usr/bin/env python3

from flask import Flask
from flask import jsonify, request
from flask_restful import Resource, Api
import json
import secrets

app = Flask(__name__)
api = Api(app)

UserList=[]
string_json = json.load(open('users.json'))

for persona in string_json:
    user = {
        "username": {persona['username']},
        "password": {persona['password']}
    }
    UserList.append(user)

#/VERSION
@app.route('/version', methods=['GET'])
def getVersion():
    return jsonify({"Version":"1.0"})

#/SIGNUP
@app.route('/signup', methods=['POST'])
def singnup():
    try:
        newUser = {
            "username": request.json['username'],
            "password": request.json['password']
        }
    except KeyError:
        return 'Introduce only the username and the password.', 400 
    userFound = [users for users in UserList if users['username'] == request.json['username']]
    if (len(userFound) > 0):
        return 'There is a user with the same name. Try other user name.', 400

    UserList.append(newUser)
    token = secrets.token_urlsafe(20)
    return jsonify({"Message": "User Added Succesfully", "User token": token})


#/LOGIN
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    for persona in UserList:
        if(f"{persona['username']}" == username and password == f"{persona['password']}"):
            return jsonify({"Message": "User is in the database"})
    else:
       return  'Username or password incorrect. Please, try it again', 400


if __name__ == '__main__':
    app.run(debug=True)