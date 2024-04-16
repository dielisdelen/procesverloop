from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify


# Scraping Imports
from case_extractor_static import scrape_case

# Database Imports
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse

# API Imports
from api.data_api import api_blueprint

# 
from dotenv import load_dotenv

# Limiter imports
from limiter_setup import init_limiter


# General imports
import json
import os

# Load environment variables
load_dotenv()

# Check if Redis Limiter is enabled
USE_REDIS_LIMITER = os.getenv('USE_REDIS_LIMITER', 'false').lower() == 'true'

# check if Async is enabled
USE_ASYNC = os.getenv('USE_ASYNC', 'false').lower() == 'true'

# loading configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REDIS_URI'] = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
app.register_blueprint(api_blueprint, url_prefix='/api')

# Import tasks after Celery has been initialized
from celery_worker import make_celery, scrape_case_task, openai_response_task, error_handler

# Initialize Celery with Flask app settings
celery = make_celery(app)

db.init_app(app)

with app.app_context():
    db.create_all()

if USE_REDIS_LIMITER:
    limiter = init_limiter(app)
else:
    # Define a dummy limiter decorator that does nothing
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    limiter = DummyLimiter()

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        ecli_id = request.form.get('ecli_id', '')

        if action == 'extract':
            existing_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
            if existing_record:
                # Record exists, so directly go to the timeline
                return redirect(url_for('timeline', ecli_id=ecli_id))
            else:
                # Chain tasks: scrape, then process with OpenAI
                (scrape_case_task.s(ecli_id) |
                 openai_response_task.s() |
                 error_handler.s()).apply_async(link_error=error_handler.s())
                # Notify user that process has started
                return jsonify({"message": "Processing started", "ecli_id": ecli_id}), 202

        pass

    return render_template('index.html')

@app.route('/timeline')
def timeline():
    ecli_id = request.args.get('ecli_id', '')
    # Now just passing ecli_id to the template, no events
    return render_template('timeline.html', ecli_id=ecli_id)

@app.route('/over')
def new_page():
    return render_template('over.html')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
