from bson.objectid import ObjectId
from datetime import datetime
from helpers.utils import is_login, is_not_login
import pymongo
import os
import hashlib
import dotenv
import middlewares.validation as validation
import time
import jwt


## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
MONGODB_URL = os.getenv('MONGODB_URL')

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
usersCol = db["users"]
blacklistCol = db["blacklist"]

## Business Logic
'''
Function for signing up a user

...

data : dict
    contains all relevant information about the user

data["username"] : string
    username of the user
    
data["password"] : string
    password of the user
    
data["email"] : string
    email of the user
    
data["first_name"] : string
    first name of the user
    
data["last_name"] : string
    last name of the user
    
data["contact"] : string
    contact number of the user
    
'''
def signup(data):
    # Create variables for easy access
    username = data['username']
    password = data['password']
    email = data['email']
    contact = data['contact']
    
    # Retrieve the hashed password
    hash = password + SECRET_KEY
    hash = hashlib.sha1(hash.encode())
    password = hash.hexdigest()
    
    # Check if account exists
    query = {
        "$or" : [
            {"username": username},
            {"email": email},
            {"contact": contact}
        ],
        "deleted_at": None
    }
    exists = usersCol.find_one(query)
    
        
    if not exists:
        # Create user document
        user_doc = {
            "username": username,
            "password": password,
            "email": email,
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "contact": contact,
            "image": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "deleted_at": None
        }
        
        # Insert user document
        result = usersCol.insert_one(user_doc)
        print(result)
        return result.acknowledged
    
    elif exists['email']==email:
        raise validation.AccountExistsException("Account already exists. Email already taken.")
    
    elif exists['username']==username:
        raise validation.AccountExistsException("Account already exists. Username already taken.")
    
    elif exists['contact']==contact:
        raise validation.AccountExistsException("Account already exists. Contact number already taken.")

    raise Exception("Did not create account.")

def login(data):
    if data['username']:
        user = data['username']
    elif data['email']:
        user = data['email']
    password = data["password"] 
    
    hash = password + SECRET_KEY
    hash = hashlib.sha1(hash.encode())
    hashed_password = hash.hexdigest()
    
    # Check if account exists
    query = {
        "$or" : [
            {"username": user},
            {"email": user},
        ],
        "password": hashed_password,
        "deleted_at": None
    }
    exists = usersCol.find_one(query, {"password": 0})
    exists["_id"] = str(exists["_id"])
    
    if not exists:
        raise validation.InvalidCredentialsException("Invalid user credentials.")
    
    is_login(exists)
    
    current_time = int(time.time())
    expiration_time = current_time + 36000 # ten hours
    claims = {
        'sub': PUBLIC_KEY,
        'exp': expiration_time,
    }
    jwt_token = jwt.encode(claims, PRIVATE_KEY, algorithm='HS256')

    # Create blacklist token
    blacklist_doc = {
        "user": ObjectId(exists["_id"]),
        "token": jwt_token,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": None
    }
    
    # Insert blacklist document
    result = blacklistCol.insert_one(blacklist_doc)
    
    finalData = exists
    finalData["token"] = jwt_token
    
    return finalData

def update_user(data):
    field = data["field"].lower()
    value = data["value"]
    
    if field == "email":
        value = validation.email_format(value)
    elif field == "username":
        value = validation.username_format(value)
    elif field == "contact":
        value = validation.contact_format(value)
    elif field == "password":
        value = validation.secure_password(value)
        
    update_query = { 
        "_id": ObjectId(data["_id"]),
        "deleted_at": None
        }
    
    new_value = {
        "$set": {
            field: value,
            "updated_at": datetime.now()
        }
    }
    
    result = usersCol.update_one(update_query, new_value)
    
    return result.acknowledged

def logout(data):
    
    existing_token = is_not_login(data)

    update_query = { "token": existing_token["token"] }
    new_value = { "$set": { "deleted_at": datetime.now() } }

    result = blacklistCol.update_one(update_query, new_value)
    print(result)
    return result.acknowledged


def get_user(data):
    # Check if account exists
    query = {
        "_id": ObjectId(data["_id"]),
        "deleted_at": None
    }
    exists = usersCol.find_one(query,{ "_id": 0, "password": 0})
    
    data["username"] = exists["username"]
    data["email"] = exists["email"]

    is_not_login(data)
    
    return exists