from flask import Blueprint, current_app
from flask_mail import Message

email_bp = Blueprint('email', __name__)

@email_bp.route("/forgot_password", methods=['POST'])
def forgot_password():
    EMAIL = current_app.config['MAIL_USERNAME']
    mail = current_app.extensions.get('mail')  # Access the mail instance
    if mail:
        msg = Message(subject='Hello from the other side!',
                      sender=EMAIL, recipients=['nealbarton307@gmail.com'])
        msg.body = "Its working, crazy"
        mail.send(msg)
        return "Message sent!"
    else:
        return "Mail service not available.", 500
