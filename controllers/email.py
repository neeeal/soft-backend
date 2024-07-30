import pymongo
import dotenv
import os
from flask_mail import Message
dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')

## Load MongoDB Client
mongoClient = pymongo.MongoClient(MONGODB_URL)

## Load MongoDB Database
db = mongoClient["dev"]

## Loading Collection
usersCol = db["users"]
blacklistCol = db["blacklist"]


def forgot_password(EMAIL, mail, DATA):
    recipient = DATA["email"]
    msg = Message(subject='Password reset',
                    sender=EMAIL, recipients=[recipient])
    msg.body = "Please follow this link to reset your password."
    mail.send(msg)

def reset_password(EMAIL, mail, DATA):
    recipient = DATA["email"]
    msg = Message(subject='Successful reset',
                    sender=EMAIL, recipients=[recipient])
    msg.body = "Your password has been reset. Please try logging in again."
    mail.send(msg)
