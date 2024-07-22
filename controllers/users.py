import pymongo
import os
import hashlib
import dotenv
from datetime import datetime
import middlewares.validation as validation
import time
import jwt
from bson.objectid import ObjectId

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
    exists = usersCol.find_one(query)
    
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
        "username": exists["username"],
        "email": exists["email"],
        "token": jwt_token,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": None
    }
    
    # Insert blacklist document
    result = blacklistCol.insert_one(blacklist_doc)
    print(result)
    
    return result.acknowledged

def update_user():
    return None

def logout(data):
    
    existing_token = is_not_login(data)

    update_query = { "token": existing_token["token"] }
    newvalues = { "$set": { "deleted_at": datetime.now() } }

    result = blacklistCol.update_one(update_query, newvalues)
    print(result)
    return result.acknowledged

def is_not_login(data):
    username = data["username"]
    email = data["email"]
    token = data["token"]
    # Check if login token exists
    query = {
        "$or" : [
            {"user": username},
            {"email": email},
        ],
        "token": token,
        "deleted_at": None
    }
    existing_token = blacklistCol.find_one(query)
    
    if not existing_token:
        raise validation.InvalidLoginTokenException("Invalid session. Please log in again.")
    
    is_expired = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])
    
    return existing_token

def is_login(data):
    username = data["username"]
    email = data["email"]
    
    # Check if login token exists
    query = {
        "$or" : [
            {"user": username},
            {"email": email},
        ],
        "deleted_at": None
    }
    existing_token = blacklistCol.find_one(query)
    
    if not existing_token:
        return None
    
    try:
        is_expired = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])
        raise validation.AlreadyLoggedInException("User is already logged in.")
    except jwt.ExpiredSignatureError:
        return None
    
def get_user(data):
    # Check if account exists
    query = {
        "_id": ObjectId(data["id"]),
        "deleted_at": None
    }
    exists = usersCol.find_one(query,{ "_id": 0, "password": 0})
    
    data["username"] = exists["username"]
    data["email"] = exists["email"]

    is_not_login(data)
    
    return exists