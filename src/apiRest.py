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
    print(document)
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
    timer = threading.Timer(300.0, revokeToken,(newToken, ))
    timer.start()

def user_exist(username):
    userFound = [users for users in UserList if users['username'] == username]
    return username

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
    userFound = user_exist(username)
    docFound = [doc for doc in DocumentList if doc['doc_id'] == doc_id]
    if(len(userFound) == 1 and len(docFound) == 0):
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
    elif (len(docFound) > 0):
        return 'The doc_id exist already! Try again with other doc_id', HTTP_400_BAD_REQUEST
    else:
        return 'The username does not exist! Try again with other username', HTTP_400_BAD_REQUEST

@app.route('/<string:username>/<string:doc_id>', methods=['PUT'])
def put(username, doc_id):
    docFound = [doc for doc in DocumentList if doc['owner'] == username and doc['doc_id'] == doc_id]
    docFound['doc_content'] = request.json['doc_content']
    
    size = sys.getsizeof(request.json['doc_content'])
    
    data = read('documents.json')
    data.append(docFound)
    write('documents.json', data)

    return jsonify({"size": size}), HTTP_201_CREATED 

@app.route('/<string:username>/<string:doc_id>', methods=['DELETE'])
def delete(username, doc_id):
    docFound = [doc for doc in DocumentList if doc['owner'] == username and doc['doc_id'] == doc_id]

    data = read('documents.json')
    data.remove(docFound)
    write('documents.json', data)
    
    return jsonify({}), HTTP_201_CREATED 

#/<string:username>/_all_docs
@app.route('/<string:user_name>/all_docs' , methods=['GET'])
def get_all_docs(user_name):
    coincidence = False
    counter = 0
    new_list=[]
    for documents in DocumentList:
        if(documents['owner']  == user_name):
            coincidence = True
            counter += 1
            document = {
                "id"+str(counter): documents['doc_id'],
                "content":documents['doc_content']
            }
            new_list.append(document)
    if coincidence == False:
        return 'The user does not have any document', HTTP_400_BAD_REQUEST
    else:
        return new_list

if __name__ == '__main__':
    app.run(debug=True, port=5000)