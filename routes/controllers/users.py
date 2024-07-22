import pymongo
import os
import hashlib
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
usersCol = db["users"]

def signup():
    print("Working Signup")    
    return None

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
