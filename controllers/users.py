import pymongo
import os
import hashlib
import dotenv
from datetime import datetime
import middlewares.validation as validation

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
MONGODB_URL = os.getenv('MONGODB_URL')

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
usersCol = db["users"]

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
    DATA = data
    # Create variables for easy access
    username = DATA['username']
    password = DATA['password']
    email = DATA['email']
    contact = DATA['contact']
    
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
            "first_name": DATA['first_name'],
            "last_name": DATA['last_name'],
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

def login():
    return None

def update_user():
    return None

def logout():
    return None

def get_user():
    return None

def create_token():
    return None
