from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.recommendation as recommendationController
import middlewares.validation as validation
import dotenv
from helpers.utils import is_not_login

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
recommendation_bp = Blueprint('recommendation',__name__)
recommendation_bp.secret_key = SECRET_KEY

@recommendation_bp.route('/skan', methods=["POST"])
def skan():
    DATA = request.get_json()    
    token = request.headers["Authorization"].split(" ")[1]
    DATA["token"] = token
    
    try:
        is_not_login(DATA)
        validation.image_data(DATA)
        result = recommendationController.get_recommendation(DATA)
    
    except validation.InvalidLoginTokenException as e:
        error_message = str(e.message)
        print(error_message)
        return jsonify({'msg': error_message}), 400

    except validation.IncorrectFieldsException as e:
        error_message = str(e.message)
        print(error_message)
        return jsonify({'msg': error_message}), 400
    
    return jsonify({
        'msg': "Successfully scanned image",
        "data": result
        }), 200
    
@recommendation_bp.route('/get_types', methods=["GET"])
def get_types():
    # DATA = request.get_json()    
    token = request.headers["Authorization"].split(" ")[1]
    user_id = request.headers.get('User-Id')  # Get user ID from headers
    DATA = {
        "token": token,
        "_id": user_id
    }
    
    try:
        is_not_login(DATA)
        result = recommendationController.get_types()
    
    except validation.InvalidLoginTokenException as e:
        error_message = str(e.message)
        print(error_message)
        return jsonify({'msg': error_message}), 400
    
    return jsonify({
        'msg': "Successfully retrieved types",
        "data": result
        }), 200