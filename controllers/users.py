from bson.objectid import ObjectId
from datetime import datetime
from helpers.utils import is_not_login
import pymongo
import os
import hashlib
import dotenv
import middlewares.validation as validation
import time
import jwt
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

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
        raise validation.AccountExistsException("Client Error. Account already exists. Email already taken.")
    
    elif exists['username']==username:
        raise validation.AccountExistsException("Client Error. Account already exists. Username already taken.")
    
    elif exists['contact']==contact:
        raise validation.AccountExistsException("Client Error. Account already exists. Contact number already taken.")

    raise Exception("Internal Server Error. Did not create account.")

def login(data):
    if data['user']:
        user = data['user']
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
    
    if not exists:
        raise validation.InvalidCredentialsException("Client Error. Invalid user credentials.")
    
    exists["_id"] = str(exists["_id"])
    

    ## false if not logged in
    # Check if login token exists
    query = {
        "user": ObjectId(exists["_id"]),
        "deleted_at": None
    }
    existing_token = list(blacklistCol.find(query).sort("created_at", -1).limit(1))
    if len(existing_token):    
        existing_token = existing_token[0]
        
        try:
            is_expired = jwt.decode(existing_token["token"], PRIVATE_KEY, algorithms=["HS256"])
            # exists["msg"] = "User is already logged in."
            exists["token"] = existing_token["token"]
            return exists
            # raise validation.AlreadyLoggedInException({
            #     "token": existing_token["token"],
            #     "message": "Client Error. User is already logged in."
            #     })
        except jwt.ExpiredSignatureError:
            print("jwt.ExpiredSignatureError")
    
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
        hash = value + SECRET_KEY
        hash = hashlib.sha1(hash.encode())
        value = hash.hexdigest()
    elif field == "image":
        # Split the value to check for file type and base64 data
        parts = value.strip().split(',')
        
        if len(parts) == 2:
            extension, file = parts
            if extension not in ['data:image/png;base64', 'data:image/jpeg;base64', 'data:image/jpg;base64']:
                return "Invalid file type. Submit only .jpg, .png, or .jpeg files."
        else:
            file = value.strip()
        
        # Handle base64 padding
        padding = len(file) % 4
        if padding:
            file += '=' * (4 - padding)
        
        try:
            image_data = base64.b64decode(file)
        except (base64.binascii.Error, ValueError) as e:
            return "Invalid image data. Could not decode base64."
        
        # Load the image, convert, and resize
        try:
            image_stream = BytesIO(image_data)
            pil_image = Image.open(image_stream).convert('RGB')
        except (IOError, ValueError) as e:
            return "Invalid image file."
        
        # Calculate new size maintaining the aspect ratio
        width, height = pil_image.size
        if width > height:
            new_width = 224
            new_height = int((height / width) * 224)
        else:
            new_height = 224
            new_width = int((width / height) * 224)
        
        save_image = pil_image.resize((new_width, new_height))
        image_stream = BytesIO()
        save_image.save(image_stream, format='JPEG')
        image_data = image_stream.getvalue()

        # Prepare image data for saving
        value = image_data
    
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
    
    exists["image"] = str(base64.b64encode(exists["image"]).decode('utf-8'))
    
    return exists