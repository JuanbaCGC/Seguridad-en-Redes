#!/usr/bin/env python3

from flask import Flask, jsonify, request, Blueprint
from flask_restful import Resource, Api
import sys
import json
import secrets
import threading
from http_status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

app = Flask(__name__)
api = Api(app)

UserList=[]
DocumentList=[]

#Read users.json
users_json = json.load(open('users.json'))
for user in users_json:
    UserList.append(user)

#Read documents.json
documents_json = json.load(open('documents.json'))
for document in documents_json:
    DocumentList.append(document)

def read(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

def write(filename, content):
    with open(filename, "w") as file:
        json.dump(content, file, indent=4)

def revokeToken(token):
    data = read('tokens.json')
    data.remove(token)
    write('tokens.json', data)

def writeToken(token, username):
    newToken = {
        "token_id":token,
        "username":username
    }
    tokens = read('tokens.json')
    tokens.append(newToken)
    write('tokens.json', tokens)
    timer = threading.Timer(5.0, revokeToken,(newToken, ))
    timer.start()

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
        return jsonify({'error': "Introduce only the username and the password."}), HTTP_400_BAD_REQUEST
        
    userFound = [users for users in UserList if users['username'] == request.json['username']]
    if (len(userFound) > 0):
        return 'There is a user with the same name. Try other user name.', HTTP_400_BAD_REQUEST
    else:
        UserList.append(newUser)

        data = read('users.json')
        data.append(newUser)
        write('users.json', data)

        token = secrets.token_urlsafe(20)
        writeToken(token,request.json['username'])
        return jsonify({"access_token": token}), HTTP_201_CREATED 

#/LOGIN
@app.route('/login', methods=['POST'])
def login():
    try:
        user = {
            "username": request.json['username'],
            "password": request.json['password']
        }
    except KeyError:
        return jsonify({'error': "Introduce only the username and the password."}), HTTP_400_BAD_REQUEST
    
    userFound = [users for users in UserList if users['username'] == request.json['username'] and users['password'] == request.json['password']]
    if(len(userFound) > 0):
        token = secrets.token_urlsafe(20)
        writeToken(token,request.json['username'])
        return jsonify({"access_token": token}), HTTP_201_CREATED 
    else:
        return 'Incorrect username or password!', HTTP_400_BAD_REQUEST

#/<string:username>/<string:doc_id>
@app.route('/<string:username>/<string:doc_id>', methods=['GET'])
def get(username, doc_id):
    docFound = [doc for doc in DocumentList if doc['owner'] == username and doc['doc_id'] == doc_id]
    return jsonify(docFound)

@app.route('/<string:username>/<string:doc_id>', methods=['POST'])
def post(username,doc_id):
    userFound = [users for users in UserList if users['username'] == username]
    documentFound = [documents for documents in DocumentList if documents['doc_id'] == doc_id]
    if(len(userFound) == 1 and len(documentFound) == 0):
        try:
            doc = {
                "owner":username,
                "doc_id":doc_id,
                "doc_content":request.json['doc_content']
            }
        except KeyError:
            return jsonify({'error': "Introduce the doc_content."}), HTTP_400_BAD_REQUEST

        DocumentList.append(doc)
        size = sys.getsizeof(request.json['doc_content'])
        
        data = read('documents.json')
        data.append(doc)
        write('documents.json', data)
        
        return jsonify({"size": size}), HTTP_201_CREATED 
    elif (len(documentFound) > 0):
        return 'The doc_id exist already! Try again with other doc_id', HTTP_400_BAD_REQUEST
    else:
        return 'The username does not exist! Try again with other username', HTTP_400_BAD_REQUEST

if __name__ == '__main__':
    app.run(debug=True, port=5000)