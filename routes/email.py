from flask import Blueprint, current_app, jsonify, request
import controllers.email as emailController
import middlewares.validation as validation

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


@email_bp.route("/reset_password", methods=['POST'])
def reset_password():
    DATA = request.get_json()    
    
    with current_app.app_context():
        EMAIL = current_app.config['MAIL_USERNAME']
        mail = current_app.extensions.get('mail')
        
        try:
            result = emailController.reset_password(EMAIL=EMAIL, mail=mail, DATA=DATA)
            
        except validation.InvalidCredentialsException as e:
            error_message = str(e.message)
            print(error_message)
            return jsonify({'msg': error_message}), 400
        
        except Exception as e:
            print("Unhandled exception")
            print(str(e))
            return jsonify({'msg': "Internal server error"}), 500
            
    return jsonify({
        'msg': "Successfully reset password.",
        'data': result
        }), 200
