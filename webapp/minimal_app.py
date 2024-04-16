from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify

# Database Imports
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models import db, ScrapeRecord, OpenAIResponse

# API Imports
from api.data_api import api_blueprint

# 
from dotenv import load_dotenv

# Limiter imports
from limiter_setup import init_limiter


from webapp.celery_config_works import celery, add_together
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['REDIS_PROD_URI'] = os.getenv('REDIS_PROD_URI')

@app.route('/')
def hello():
    result = add_together.delay(23, 42)
    return 'Task submitted! Check your worker console for the result.'

if __name__ == '__main__':
    app.run(debug=True)