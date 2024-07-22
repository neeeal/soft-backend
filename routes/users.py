from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.users as usersController
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
users_bp = Blueprint('users',__name__)
users_bp.secret_key = SECRET_KEY

@users_bp.route('/signup', methods=['POST'])
def signup():
    DATA = request.get_json()
    return None

@users_bp.route('/login', methods=['POST'])
def login():
    return None

@users_bp.route('/update_user', methods = ['GET', 'PUT'])
def update_user():
    return None

@users_bp.route("/logout", methods=['POST'])
def logout():
    return None

@users_bp.route("/get_user", methods=["GET"])
def get_user():
    return None

@users_bp.route('/token', methods=["POST"])
def create_token():
    return None
