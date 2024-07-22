from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.history as historyController
import middlewares.validation as validation
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
history_bp = Blueprint('history',__name__)
history_bp.secret_key = SECRET_KEY

@history_bp.route("/get_history_with_images", methods=["GET"])
def get_history_with_images():
    return None
    
@history_bp.route("/get_history_entry/<int:history_id>", methods=["GET"])
def get_history_entry(history_id):
    return None