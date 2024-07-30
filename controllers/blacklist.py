import pymongo
import dotenv
import os
import jwt
import middlewares.validation as validation

dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
blacklistCol = db["blacklist"]

def verify_token(DATA):
    jwt_token = DATA["token"]
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
    
    return {"token": existing_token["token"]}