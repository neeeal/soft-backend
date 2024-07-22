from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.users as usersController
import middlewares.validation as validation
import dotenv

## Connect to Flask
users_bp = Blueprint('users',__name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    DATA = request.get_json()    
    
    try:
        complete_data = validation.signup_data(DATA)
        correct_method = validation.is_POST(request.method)
        result = usersController.signup(complete_data)
                
    except validation.IncorrectMethodException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.IncorrectFieldsException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.IncorrectFormatException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.IncorrectDataException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.AccountExistsException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
        
    return jsonify({
        'msg': "Successfully registered user.",
        'data': result
        }), 400

@users_bp.route('/login', methods=['POST'])
def login():
    usersController.login()
    return None

@users_bp.route('/update_user', methods = ['GET', 'PUT'])
def update_user():
    usersController.update_user()
    return None

@users_bp.route("/logout", methods=['POST'])
def logout():
    usersController.logout()
    return None

@users_bp.route("/get_user", methods=["GET"])
def get_user():
    usersController.get_user()
    return None

@users_bp.route('/token', methods=["POST"])
def create_token():
    usersController.create_token()
    return None
