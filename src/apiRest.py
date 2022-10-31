#!/usr/bin/env python3

from flask import Flask, jsonify, request, Blueprint
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
def signup():
	try:
		newUser = {
			"username": request.json['username'],
			"password": request.json['password']
		}
	except KeyError:
		return jsonify({'error': "Introduce only the username and the password."}), 400
        
	userFound = [users for users in UserList if users['username'] == request.json['username']]
	if (len(userFound) > 0):
		return 'There is a user with the same name. Try other user name.', 400

	UserList.append(newUser)
	token = secrets.token_urlsafe(20)
	return jsonify({"Message": "User Added Succesfully", "User token": token}), 201


#/LOGIN
@app.route('/login', methods=['POST'])
def login():
	try:
		user = {
			"username": request.json['username'],
			"password": request.json['password']
		}
	except KeyError:
		return jsonify({'error': "Introduce only the username and the password."}), 400
	
	userFound = [users for users in UserList if user['username'] == request.json['username'] and user['password'] == request.json['password']]
	if(len(userFound) > 0):
		token = secrets.token_urlsafe(20)
		return jsonify({"Message": "User Login Succesfully", "User token": token}), 201 
	else:
		return 'Incorrect username or password!', 400

if __name__ == '__main__':
	app.run(debug=True, port=5000)
