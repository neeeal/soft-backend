from flask import Blueprint, current_app, jsonify, request
import controllers.email as emailController
import middlewares.validation as validation
import jwt

email_bp = Blueprint('email', __name__)

@email_bp.route("/forgot_password", methods=['POST'])
def forgot_password():
    DATA = request.get_json()    
    
    with current_app.app_context():
        EMAIL = current_app.config['MAIL_USERNAME']
        mail = current_app.extensions.get('mail')
        
        try:
            result = emailController.forgot_password(EMAIL=EMAIL, mail=mail, DATA=DATA)
            
        except validation.InvalidCredentialsException as e:
            error_message = str(e.message)
            print(error_message)
            return jsonify({'msg': error_message}), 400
        
        except Exception as e:
            print("Unhandled exception")
            print(str(e))
            return jsonify({'msg': "Internal server error"}), 500
            
    return jsonify({
        'msg': "Successfully sent to email.",
        'data': result
        }), 200


@email_bp.route("/reset_password/<string:token>", methods=['POST'])
def reset_password(token):
    DATA = request.get_json()   
    DATA['token'] = token 
    
    with current_app.app_context():
        EMAIL = current_app.config['MAIL_USERNAME']
        mail = current_app.extensions.get('mail')
        
        try:
            result = emailController.reset_password(EMAIL=EMAIL, mail=mail, DATA=DATA)
            
        except validation.InvalidCredentialsException as e:
            error_message = str(e.message)
            print(error_message)
            return jsonify({'msg': error_message}), 400
        
        except jwt.ExpiredSignatureError:
            error_message = str("Session expired. Please try again later.")
            print(error_message)
            return jsonify({'msg': error_message}), 401
        
        except Exception as e:
            print("Unhandled exception")
            print(str(e))
            return jsonify({'msg': "Internal server error"}), 500
            
    return jsonify({
        'msg': "Successfully reset password.",
        'data': result
        }), 200
