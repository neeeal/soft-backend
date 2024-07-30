from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
import os
import dotenv
from datetime import timedelta

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config["SESSION_TYPE"] = "filesystem"
EMAIL = os.getenv("MAIL_USERNAME")
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL")
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

mail = Mail(app)
CORS(app)

from routes.history import history_bp
from routes.recommendation import recommendation_bp
from routes.users import users_bp
from routes.blacklist import blacklist_bp
from routes.email import email_bp

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')
app.register_blueprint(blacklist_bp, url_prefix='/api/blacklist')
app.register_blueprint(email_bp, url_prefix='/api/email')

@app.route('/api')
def index():
    return jsonify({'msg': 'API is now online'}), 200

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=os.getenv("PORT", default=5000))
