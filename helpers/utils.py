import pymongo
import os
import dotenv
import middlewares.validation as validation
import jwt
from bson.objectid import ObjectId

## Loading Envieronment Variables
dotenv.load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
MONGODB_URL = os.getenv('MONGODB_URL')

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
blacklistCol = db["blacklist"]

def is_not_login(data):
    ## True if not logged in
    token = data["token"]
    # Check if login token exists
    query = {
        "user": ObjectId(data["_id"]),
        "token": token,
        "purpose": "login",
        "deleted_at": None
    }
    existing_token = blacklistCol.find_one(query)
    
    if not existing_token:
        raise validation.InvalidLoginTokenException("Client Error. Invalid session. Please log in again.")
    
    is_expired = jwt.decode(token, PRIVATE_KEY, algorithms=["HS256"])
    
    return existing_token

# def is_login(data):
#     ## false if not logged in
#     # Check if login token exists
#     query = {
#         "user": ObjectId(data["_id"]),
#         "deleted_at": None
#     }
#     existing_token = list(blacklistCol.find(query).sort("created_at", -1).limit(1))
#     if not len(existing_token):
#         return None
    
#     existing_token = existing_token[0]
    
#     try:
#         is_expired = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])
#         raise validation.AlreadyLoggedInException({
#             "token": existing_token["token"],
#             "message": "Client Error. User is already logged in."
#             })
#     except jwt.ExpiredSignatureError:
#         print("jwt.ExpiredSignatureError")
#         return None
    