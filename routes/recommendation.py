from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.recommendation as recommendationController
import middlewares.validation as validation
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
recommendation_bp = Blueprint('recommendation',__name__)
recommendation_bp.secret_key = SECRET_KEY

@recommendation_bp.route('/skan', methods=["POST"])
def skan():
    return None