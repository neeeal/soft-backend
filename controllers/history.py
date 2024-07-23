import pymongo
import os
import dotenv
import base64
import jwt
from helpers.utils import is_not_login
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
historyCol = db["history"]
blacklistCol = db["blacklist"]
stressCol = db["stress"]

def get_history_with_images(data):
    blacklist_query = {
        "user": data["user_id"],
        "token": data["token"],
        "deleted_at": None
    }
    token = blacklistCol.find(blacklist_query)
    
    history_query = {
        "user": ObjectId(data["user_id"]),
        "deleted_at": None
    }
    cursor = historyCol.find(history_query)
    
    stress_query = {
        "deleted_at": None
    }
    stress_cursor = stressCol.find(stress_query, {
        "stress_type": 1, 
        "stress_name": 1,
        "stress_level": 1,
        "description": 1,
        "recommendation": 1,
        "recommendation_src": 1,
        "description_src": 1
    })
    
    stresses = [x for x in stress_cursor]
    
    results = []
    for result in cursor:
        result["user"] = str(result["user"])
        result["_id"] = str(result["_id"])
        result["rice_image"] = str(base64.b64encode(result["rice_image"]).decode('utf-8'))
        
        stress = stresses[result["stress_id"]-1]
        
        result["stress_type"] = stress["stress_type"]
        result["stress_name"] = stress["stress_name"]
        result["stress_level"] = stress["stress_level"]
        result["description"] = stress["description"]
        result["recommendation"] = stress["recommendation"]
        result["recommendation_src"] = stress["recommendation_src"]
        result["description_src"] = stress["description_src"]
        results.append(result)
        
    return results