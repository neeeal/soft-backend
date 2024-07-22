from flask import Flask, render_template, redirect, request, jsonify, session, send_file, Blueprint
import os
import controllers.blacklist as blacklistController
import middlewares.validation as validation
import dotenv

## Loading Envieronment Variables
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

## Connect to Flask
blacklist_bp = Blueprint('blacklist',__name__)
blacklist_bp.secret_key = SECRET_KEY