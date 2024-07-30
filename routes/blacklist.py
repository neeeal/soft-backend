from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import jwt
import controllers.blacklist as blacklistController
import middlewares.validation as validation
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
blacklist_bp = Blueprint('blacklist',__name__)
blacklist_bp.secret_key = SECRET_KEY

@blacklist_bp.route("/verify_token/<string:token>", methods=['GET'])
def verify_token(token):
    DATA = {
        "token": token
    } 
    try: 
        result = blacklistController.verify_token(DATA)
        
    except jwt.ExpiredSignatureError:
        error_message = str("Session expired. Please try again later.")
        print(error_message)
        return jsonify({'msg': error_message}), 401

    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
    
    return jsonify({
        'msg': "Successfully verified token.",
        'data': result
        }), 200