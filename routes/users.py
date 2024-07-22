from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.users as usersController
import controllers.blacklist as blacklistController
import middlewares.validation as validation
import dotenv
import jwt 

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
        }), 200

@users_bp.route('/login', methods=['POST'])
def login():
    DATA = request.get_json()    
    
    try: 
        correct_method = validation.is_POST(request.method)
        complete_data = validation.login_data(DATA)
        result = usersController.login(complete_data)
        
    except validation.IncorrectMethodException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.InvalidCredentialsException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.AlreadyLoggedInException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
    
    return jsonify({
        'msg': "Successfully logged in.",
        'data': result
        }), 200

@users_bp.route('/update_user', methods = ['PUT'])
def update_user():
    DATA = request.get_json()    
    
    try:
        correct_method = validation.is_PUT(request.method)
        result = usersController.update_user(DATA)
    
    except validation.IncorrectDataException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
    
    return jsonify({
            'msg': "Succesfully updated user.",
            'data': result
            }), 200

@users_bp.route("/logout", methods=['POST'])
def logout():
    DATA = request.get_json()    

    try: 
        correct_method = validation.is_POST(request.method)
        result = usersController.logout(DATA)

    except validation.IncorrectMethodException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except validation.InvalidLoginTokenException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400

    except jwt.ExpiredSignatureError:
        error_message = str("Session expired. Please login again.")
        return jsonify({'msg': error_message}), 400

    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500

    return jsonify({
            'msg': "Successfully logged out.",
            'data': result
            }), 200

@users_bp.route("/get_user/<string:user_id>", methods=["GET"])
def get_user(user_id):
    token = request.headers["Authorization"].split(" ")[1]
    
    DATA = {"_id": user_id, "token": token}
    
    try:
        correct_method = validation.is_GET(request.method)
        result = usersController.get_user(DATA)
    
    except validation.InvalidLoginTokenException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400

    except validation.IncorrectMethodException as e:
        error_message = str(e.message)
        return jsonify({'msg': error_message}), 400
    
    except Exception as e:
        print("Unhandled exception")
        print(str(e))
        return jsonify({'msg': "Internal server error"}), 500
    
    return jsonify({
        'msg': "Successfully retrieved data.",
        'data': result
        }), 200
    