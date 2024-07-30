import pymongo
import dotenv
import time
import os
import jwt
import hashlib
import middlewares.validation as validation
from datetime import datetime
from bson.objectid import ObjectId
from flask_mail import Message

dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
usersCol = db["users"]
blacklistCol = db["blacklist"]

def forgot_password(EMAIL, mail, DATA):
    recipient = DATA["email"].lower()

    query = {
        "email": recipient,
        "deleted_at": None
    }

    user_doc = usersCol.find_one(query)

    if user_doc is None:
        raise validation.InvalidCredentialsException("Client Error. User does not exist.")
    
    query = {
        "user": ObjectId(user_doc["_id"]),
        "deleted_at": None,
        "purpose": "forgot_password"
    }
    
    existing_token = list(blacklistCol.find(query).sort("created_at", -1).limit(1))
    if len(existing_token):    
        existing_token = existing_token[0]
        
        try:
            decoded_token = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])
            update_query = { "token": existing_token["token"] }
            new_value = { "$set": { "deleted_at": datetime.now() } }
            result = blacklistCol.update_one(update_query, new_value)
    
        except jwt.ExpiredSignatureError:
            print("jwt.ExpiredSignatureError")
    
    current_time = int(time.time())
    expiration_time = current_time + 600 # ten minutes
    claims = {
        'sub': PUBLIC_KEY,
        'exp': expiration_time
    }
    jwt_token = jwt.encode(claims, PRIVATE_KEY, algorithm='HS256')

    # Create blacklist token
    blacklist_doc = {
        "user": ObjectId(user_doc["_id"]),
        "token": jwt_token,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": None,
        "purpose": "forgot_password"
    }
    
    # Insert blacklist document
    result = blacklistCol.insert_one(blacklist_doc)
    
    msg = Message(subject='Password reset',
                    sender=EMAIL, recipients=[recipient])
    msg.body = "Please follow this link to reset your password. {}".format(jwt_token)
    mail.send(msg)
    
    return None

def reset_password(EMAIL, mail, DATA):
    jwt_token = DATA["token"]
    password = DATA["new_password"]

    query = {
        "token": jwt_token,
        "deleted_at": None,
        "purpose": "forgot_password"
    }
    
    existing_token = list(blacklistCol.find(query).sort("created_at", -1).limit(1))
    
    if len(existing_token):    
        existing_token = existing_token[0]
        decoded_token = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])

    else:
        raise validation.InvalidCredentialsException("Client Error. Token does not exist.")
    
    update_query = { "token": existing_token["token"] }
    new_value = { "$set": { "deleted_at": datetime.now() } }
    result = blacklistCol.update_one(update_query, new_value)
    
    query = {
        "_id": existing_token["user"],
        "deleted_at": None
    }

    user_doc = usersCol.find_one(query)
    
    update_query = { 
        "_id": ObjectId(user_doc["_id"]),
        "deleted_at": None
    }
    
    value = validation.secure_password(password)
    hash = value + SECRET_KEY
    hash = hashlib.sha1(hash.encode())
    hashed_password = hash.hexdigest()
    
    new_value = {
        "$set": {
            "password": hashed_password,
            "updated_at": datetime.now()
        }
    }
    
    result = usersCol.update_one(update_query, new_value)

    if user_doc is None:
        raise validation.InvalidCredentialsException("Client Error. User does not exist.")
    
    msg = Message(subject='Successful reset',
                    sender=EMAIL, recipients=[user_doc["email"]])
    msg.body = "Your password has been reset. Please try logging in again."
    mail.send(msg)
    
    return None
