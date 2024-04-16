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

# Celery import
from celery import Celery

# General imports
import json
import os
import logging

# Load environment variables
load_dotenv()

# Set up basic logging for celery
if os.getenv('LOGGING_ENABLED', 'false').lower() == 'true':
    logging.basicConfig(filename='/run/procesverloop-logs/celery.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
logging.info("Logging initialized")

# Check if Redis Limiter is enabled
USE_REDIS_LIMITER = os.getenv('USE_REDIS_LIMITER', 'false').lower() == 'true'

# loading configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REDIS_URI'] = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
app.register_blueprint(api_blueprint, url_prefix='/api')

# Initialize Celery with Flask app settings
def make_celery(app):
    logging.info("Initializing celery")
    redis_uri = app.config['REDIS_URI']
    celery = Celery(app.import_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Change to 'optional' or 'none' as per your Redis setup and security requirements
    }

    celery.conf.update({
        'broker_url': redis_uri,
        'result_backend': redis_uri,
        'broker_use_ssl': ssl_options,
        'redis_backend_use_ssl': ssl_options,
        'task_default_queue': 'celery{my_app}',
        'task_default_exchange': 'celery{my_app}',
        'task_default_routing_key': 'celery{my_app}',
    })

    # Ensure that tasks are executed in the Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

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

@celery.task
def scrape_case_task(ecli_id):
    logging.info(f"Starting scrape_case_task for ECLI ID: {ecli_id}")
    metadata, extracted_text = scrape_case(ecli_id)
    if extracted_text != "Error during navigation or data retrieval." and extracted_text != "Error during parsing.":
        logging.info(f"Scraping successful, saving data for ECLI ID: {ecli_id}")
        new_record = ScrapeRecord(metadata=metadata, raw_text=extracted_text)
        db.session.add(new_record)
        db.session.commit()
        logging.info(f"Data saved for ECLI ID: {ecli_id}")
    else:
        logging.info(f"Scraping failed for ECLI ID: {ecli_id}, Error: {extracted_text}")
    return ecli_id, extracted_text
    pass

@celery.task
def openai_response_task(ecli_id, extracted_text):
    logging.info(f"Sending data to OpenAI for ECLI ID: {ecli_id}")
    response_content = get_openai_response(ecli_id, extracted_text)
    logging.info(f"Received response from OpenAI for ECLI ID: {ecli_id}")
    return ecli_id, response_content
    pass

@celery.task
def add(x, y):
    return x + y


@celery.task
def error_handler(uuid):
    logging.info(f'Task {uuid} raised exception!')
    pass

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
                 openai_response_task.s(ecli_id) |
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
