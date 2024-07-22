from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.history as historyController
import middlewares.validation as validation
import dotenv
import jwt

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
history_bp = Blueprint('history',__name__)
history_bp.secret_key = SECRET_KEY

@history_bp.route("/get_history_with_images", methods=["GET"])
def get_history_with_images():
    user_id = request.headers.get('User-Id')  # Get user ID from headers
    data = {
        "user_id": user_id,
        "token": request.headers.get('Authorization').split(" ")[1]  # Get token from headers
    }
    try:
        result = historyController.get_history_with_images(data)

    except validation.IncorrectMethodException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400

    except jwt.ExpiredSignatureError:
        error_message = str("Session expired. Please login again.")
        return jsonify({'msg': error_message}), 401
    
    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
        
    return jsonify({
        'msg': "Successfully retrieved history user.",
        'data': result
        }), 200
    
@history_bp.route("/get_history_entry/<int:history_id>", methods=["GET"])
def get_history_entry(history_id):
    return None