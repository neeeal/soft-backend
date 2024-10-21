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

def get_latest_home_data(data):
    blacklist_query = {
        "user": data["user_id"],
        "token": data["token"],
        "purpose": "login",
        "deleted_at": None
    }
    token = blacklistCol.find(blacklist_query)
    
    history_query = {
        "user": ObjectId(data["user_id"]),
        "deleted_at": None
    }
    history_cursor = historyCol.find(history_query).sort("date_transaction", -1).limit(3)
    
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
        "description_src": 1,
        "rice_image": 1
    })
    
    histories = []
    stresses = []
    
    for stress in stress_cursor:
        stress["_id"] = str(stress["_id"])
        stress["stress_type"] = stress["stress_type"].title()
        stress["stress_name"] = stress["stress_name"].title()
        stress["rice_image"] = str(base64.b64encode(stress["rice_image"]).decode('utf-8'))
        stress["recommendation"] = stress["recommendation"].replace("\\n", "\n\n")
        stress["description"] = stress["description"].replace("\\n", "\n\n")
        stresses.append(stress)
        
    print("sucesss types retrieval")
    for history in history_cursor:
        history["_id"] = str(history["_id"])
        history["user"] = str(history["user"])
        history["rice_image"] = str(base64.b64encode(history["rice_image"]).decode('utf-8'))
        
        print(history["stress_id"]-1)
        stress = stresses[history["stress_id"]-1]
        
        history["stress_level"] = stress["stress_level"]
        history["description"] = stress["description"].replace("\\n", "\n\n")
        history["recommendation"] = stress["recommendation"].replace("\\n", "\n\n")
        history["recommendation_src"] = stress["recommendation_src"]
        history["description_src"] = stress["description_src"]
        histories.append(history)
    print("sucesss history retrieval")
    
    data = {
        "history": histories,
        "types": stresses[:3]
    }
    return data


def get_stress(data):
    blacklist_query = {
        "user": data["user_id"],
        "token": data["token"],
        "purpose": "login",
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
    print("sucesss types retrieval")
    
    results = []
    for result in cursor:
        result["user"] = str(result["user"])
        result["_id"] = str(result["_id"])
        result["rice_image"] = str(base64.b64encode(result["rice_image"]).decode('utf-8'))
        
        print(result["stress_id"]-1)
        stress = stresses[result["stress_id"]-1]
        
        result["stress_type"] = stress["stress_type"].title()
        result["stress_name"] = stress["stress_name"].title()
        result["stress_level"] = stress["stress_level"]
        result["description"] = stress["description"].replace("\\n", "\n\n")
        result["recommendation"] = stress["recommendation"].replace("\\n", "\n\n")
        result["recommendation_src"] = stress["recommendation_src"]
        result["description_src"] = stress["description_src"]
        results.append(result)
    print("sucesss history retrieval")
        
    return results

def get_history_with_images(data):
    blacklist_query = {
        "user": data["user_id"],
        "token": data["token"],
        "purpose": "login",
        "deleted_at": None
    }
    token = blacklistCol.find(blacklist_query)
    
    history_query = {
        "user": ObjectId(data["user_id"]),
        "deleted_at": None
    }
    history_cursor = historyCol.find(history_query).sort("date_transaction", -1)
    
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
    print("sucesss types retrieval")
    
    results = []
    for result in history_cursor:
        result["user"] = str(result["user"])
        result["_id"] = str(result["_id"])
        result["rice_image"] = str(base64.b64encode(result["rice_image"]).decode('utf-8'))
        
        result['date_transaction'] = result['date_transaction'].strftime("%B %d, %Y %H:%M")
        
        stress = stresses[result["stress_id"]-1]
        
        result["stress_type"] = stress["stress_type"].title()
        result["stress_name"] = stress["stress_name"].title()
        result["stress_level"] = stress["stress_level"]
        result["description"] = stress["description"].replace("\\n", "\n\n")
        result["recommendation"] = stress["recommendation"].replace("\\n", "\n\n")
        result["recommendation_src"] = stress["recommendation_src"]
        result["description_src"] = stress["description_src"]

        results.append(result)
    print("sucesss history retrieval")
        
    return {"history": results}