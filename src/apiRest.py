#!/usr/bin/env python3

from flask import Flask, jsonify, request, Blueprint
import os
from flask_restful import Resource, Api
import sys
import json
import uuid
import hashlib
import secrets
import threading
from werkzeug.exceptions import BadRequest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from json.decoder import JSONDecodeError
from http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, MAX_DOCUMENTS

app = Flask(__name__)
api = Api(app)
root = "/home/kali/.practica3/Seguridad-en-Redes/src"
limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["30 per minute"]
    )

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

# Method that read the input filename
def read(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

# Method that write in the input filename
def write(filename, content):
    with open(filename, "w") as file:
        json.dump(content, file, indent=4)

# Method that revoke a token after five minutes of its creation
def revokeToken(token):
    data = read('tokens.json')
    data.remove(token)
    write('tokens.json', data)

# Method that write a token in the tokens.json
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

# Method that search if the token given is correct
def verifyToken(token):
    data = read('tokens.json')
    for saved_token in data:
        if (saved_token['token_id'] == token):
            return (True,saved_token['username'])
    return (False,'The token does not exist')

# Method that provide the errors if the Authorization header is incorrect
def verifyHeader(username):
    #Get the Authorization header (the first position is "token", the second is the user_token) and verify the structure
    header = request.headers.get('Authorization')
    if(header is None):
        return jsonify({'error': "Header is empty. Enter authorization"}), HTTP_401_UNAUTHORIZED
    else:
        authHeader = header.split()
        if(len(authHeader) != 2 or authHeader[0] != "token"):
            return jsonify({'error': "Incorrect authorization header. Try again with the following format: token user_token."}), HTTP_400_BAD_REQUEST

        #Verify that the token exist and it belongs to the user that do the request
        token_exist = verifyToken(authHeader[1])
        user_name = token_exist[1]
        if(token_exist[0] == False or user_name != username):
            return jsonify({'error': "Incorrect token."}), HTTP_403_FORBIDDEN
        else:
            return True,'The authorization header is correct.'

#Hashing function for a password using a random unique salt
def hashPass(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

# Method to compare the hash stored in the users.json and the provided password and see if they match
def matchHashedText(hashedPass, providedPass):
    #Check for the password in the hashed password
    _hashedPass, salt = hashedPass.split(':')
    return _hashedPass == hashlib.sha256(salt.encode() + providedPass.encode()).hexdigest()

# Method to clear the tokens.json
def clearTokens():
    write('tokens.json', [])

#/VERSION
@app.route('/version', methods=['GET'])
def getVersion():
    return jsonify({"Version":"1.0"}), HTTP_200_OK

#/SIGNUP
@app.route('/signup', methods=['POST'])
@limiter.limit("30 per minute", key_func = lambda : request.get_json(force=True)['username'])
def signup():
    try:
        parameters = request.get_json(force=True)
        newUser = {
            "username": str(parameters['username']),
            "hash-salt": hashPass(str(parameters['password']))
        }
    except KeyError:
        return jsonify({'error': "Introduce only the username and the password."}), HTTP_400_BAD_REQUEST
        
    userFound = [users for users in UserList if users['username'] == request.json['username']]
    if (len(userFound) > 0):
        return jsonify({'error': "There is a user with the same name. Try other user name."}), HTTP_403_FORBIDDEN
    else:
        UserList.append(newUser)
        data = read('users.json')
        data.append(newUser)
        write('users.json', data)

        os.mkdir(root+"/"+request.json['username'])
        token = secrets.token_urlsafe(20)
        writeToken(token,request.json['username'])
        return jsonify({"access_token": token}), HTTP_201_CREATED

#/LOGIN
@app.route('/login', methods=['POST'])
@limiter.limit("30 per minute", key_func = lambda : request.get_json(force=True)['username'])
def login():
    try:
        parameters = request.get_json(force=True)
        userFound = [users for users in UserList if users['username'] == str(parameters['username']) and matchHashedText(users['hash-salt'],str(parameters['password']))]
    except KeyError:
        return jsonify({'error': "Introduce only the username and the password."}), HTTP_400_BAD_REQUEST
    if(len(userFound) > 0):
        token = secrets.token_urlsafe(20)
        writeToken(token,str(parameters['username']))
        return jsonify({"access_token": token}), HTTP_201_CREATED 
    else:
        return jsonify({'error': "Incorrect username or password!"}), HTTP_403_FORBIDDEN

#GET DOCUMENT
#/<string:username>/<string:doc_id>
@app.route('/<string:username>/<string:doc_id>', methods=['GET'])
def get(username, doc_id):
    validate = verifyHeader(username)
    if(validate[0] == True):
        documents_list = os.listdir(root+"/"+username)
        if doc_id not in documents_list:
            return jsonify({'error': "The user "+username+" does not have any document with this name."}), HTTP_404_NOT_FOUND
        else:
            file = open(root+"/"+username+"/"+doc_id, "r")
            return jsonify(json.load(file)), HTTP_200_OK
    else:
        return validate

#POST DOCUMENT
@app.route('/<string:username>/<string:doc_id>', methods=['POST'])
def post(username,doc_id):
    validate = verifyHeader(username)
    if(validate[0] == True):
        documents_list = os.listdir(root+"/"+username)
        if len(documents_list) == MAX_DOCUMENTS:
            return jsonify({'error': "You have the maximum number of documents ("+str(MAX_DOCUMENTS)+"). If you want to create another one, you must delete other document."}), HTTP_400_BAD_REQUEST    
        if doc_id in documents_list:
            return jsonify({'error': "You have another document with this doc_id! Try again with other doc_id."}), HTTP_400_BAD_REQUEST
        else:
            try:
                parameters = request.get_json(force=True)
            except BadRequest:
                return jsonify({'error': "Introduce the doc_content with a json struct."}), HTTP_400_BAD_REQUEST
            try:
                content = json.dumps(parameters['doc_content'])
            except TypeError:
                return jsonify({'error': "Introduce the doc_content with a json struct."}), HTTP_400_BAD_REQUEST
            except KeyError:
                return jsonify({'error': "Introduce the doc_content."}), HTTP_400_BAD_REQUEST
            file = open(root+"/"+username+"/"+doc_id, "w")
            file.write(str(content))
            size = sys.getsizeof(str(content))
            return jsonify({"size": size}), HTTP_201_CREATED 
    else:
        return validate

#PUT DOCUMENT
@app.route('/<string:username>/<string:doc_id>', methods=['PUT'])
def put(username, doc_id):
    validate = verifyHeader(username)
    if(validate[0] == True):
        documents_list = os.listdir(root+"/"+username)
        if doc_id not in documents_list:
            return jsonify({'error': "The document "+doc_id+" does not exist! Try again with other doc_id."}), HTTP_404_NOT_FOUND
        else:
            try:
                parameters = request.get_json(force=True)
            except BadRequest:
                return jsonify({'error': "Introduce the doc_content with a json struct."}), HTTP_400_BAD_REQUEST
            try:
                content = json.dumps(parameters['doc_content'])
            except TypeError:
                return jsonify({'error': "Introduce the doc_content with a json struct."}), HTTP_400_BAD_REQUEST
            except KeyError:
                return jsonify({'error': "Introduce the doc_content."}), HTTP_400_BAD_REQUEST
            file = open(root+"/"+username+"/"+doc_id, "w")
            file.write(str(content))
            size = sys.getsizeof(str(content))
            return jsonify({"size": size}), HTTP_201_CREATED 
    else:
        return validate

#DELETE DOCUMENT
@app.route('/<string:username>/<string:doc_id>', methods=['DELETE'])
def delete(username, doc_id):
    validate = verifyHeader(username)
    if(validate[0] == True):
        documents_list = os.listdir(root+"/"+username)
        if doc_id not in documents_list:
            return jsonify({'error': "The document "+doc_id+" does not exist! Try again with other doc_id."}), HTTP_404_NOT_FOUND
        else:
            os.remove(root+"/"+username+"/"+doc_id)
        return jsonify({}), HTTP_200_OK 
    else:
        return validate

#GET ALL DOCS
#/<string:username>/_all_docs
@app.route('/<string:username>/_all_docs' , methods=['GET'])
def get_all_docs(username):
    validate = verifyHeader(username)
    if(validate[0] == True):
        if os.path.exists(root+"/"+username):
            if len(os.listdir(root+"/"+username)) == 0:
                return jsonify({'error': "You don't have any document."}), HTTP_404_NOT_FOUND
            else:
                documents_found={}
                for filename in os.listdir(root+"/"+username):
                    file = open(root+"/"+username+"/"+filename, "r")
                    documents_found[filename] = json.load(file)
                return jsonify(documents_found), HTTP_200_OK 
        else:
            return jsonify({'error': "Username does not exist."}), HTTP_404_NOT_FOUND
    else:
        return validate

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    app.teardown_appcontext(clearTokens())
    