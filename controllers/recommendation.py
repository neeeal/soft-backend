from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import gdown
import requests
import base64
from io import BytesIO
import pymongo
import dotenv
import os
from bson.objectid import ObjectId
from datetime import datetime
import calendar
import helpers.recommendation as recommendation_helper

dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
mongoClient = pymongo.MongoClient(MONGODB_URL)
db = mongoClient["dev"]
stressCol = db["stress"]
historyCol = db["history"]

image_size = (224)
channels = 3
model=None

def get_types():
    query = {
        "deleted_at": None
    }
    
    stress_docs = stressCol.find(query)
    
    results = []
    for stress_doc in stress_docs:
        stress_doc["_id"] = str(stress_doc["_id"])
        stress_doc["recommendation"] = stress_doc["recommendation"].replace("\\n", "\n\n")
        stress_doc["description"] = stress_doc["description"].replace("\\n", "\n\n")
        stress_doc["rice_image"] = str(base64.b64encode(stress_doc["rice_image"]).decode('utf-8'))
        results.append(stress_doc)
        
    return {"types":results}


# Define the function to handle the KerasLayer when loading the model
def get_recommendation(DATA):
    
    if len(DATA['image'].strip().split(',')) == 2:
        extension, file = DATA['image'].strip().split(',')
        if extension not in ['data:image/png;base64','data:image/jpeg;base64','data:image/jpg;base64'] : 
            msg = "Invalid file type. Submit only .jpg, .png, or .jpeg files."
            return jsonify({"msg":msg}), 400
        padding = len(file) % 4
        if padding:
            file += '=' * (4 - padding)
        image_data = base64.b64decode(file)
    else:
        file = DATA['image'].strip()
        padding = len(file) % 4
        if padding:
            file += '=' * (4 - padding)
        image_data = base64.b64decode(file)
    image_stream = BytesIO(image_data)
    pil_image = Image.open(image_stream
                            ).convert('RGB')
    width, height = pil_image.size
    if width > height:
        new_width = 224
        new_height = int((height/width)*224)
    else:
        new_height = 224
        new_width = int((width/height)*224)
    new_size = (new_width, new_height)
    save_image = pil_image.resize(new_size)
    image_stream = BytesIO()
    save_image.save(image_stream, format='JPEG')
    image_data = image_stream.getvalue()
    data = np.array(pil_image)

    ## Image for saving
    rice_image = image_data

    ## Model prediction
    global model
    if model == None:
        model = recommendation_helper.load_m()
    data = recommendation_helper.preprocessData(data)
    result = np.argmax(model(data))+1

    ## Getting Recommendation using output from model
    stress_id = int(result)
    
    query = {
        "stress_id": stress_id,
        "deleted_at": None
    }
    
    stress_doc = stressCol.find_one(query, {"_id": 0, "stress_id": 0, "rice_image": 0})
    stress_doc["recommendation"] = stress_doc["recommendation"].replace("\\n", "\n\n")
    stress_doc["description"] = stress_doc["description"].replace("\\n", "\n\n")
    
    now = datetime.now()
    history_doc = {
        "user": ObjectId(DATA["_id"]),
        "stress_id": stress_id,
        "date_transaction": now, ## created_at
        "updated_at":now,
        "deleted_at": None,
        "rice_image": rice_image,
        "image_name": f"{DATA['_id'][-10:]}_{calendar.timegm(now.timetuple())}_{stress_id}",
    }
    
    # Insert user document
    result = historyCol.insert_one(history_doc)
    
    history_doc["user"] = str(history_doc["user"])
    history_doc["_id"] = str(history_doc["_id"])
    history_doc["rice_image"] = str(base64.b64encode(history_doc["rice_image"]).decode('utf-8'))
    
    return history_doc | stress_doc