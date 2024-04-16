from celery import Celery
from flask import current_app  # You will not use this directly, it's shown just for context
from case_extractor_static import scrape_case
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse
from datetime import datetime
import os
import logging

# Create a Celery instance as a global variable
celery = Celery(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def make_celery(app):
    app_name = 'webapp'
    # Configure the global celery instance with Flask app settings
    redis_uri = 'rediss://pvredis-a42qr8.serverless.eun1.cache.amazonaws.com:6379'
    celery = Celery(app_name, broker=redis_uri, backend=redis_uri)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

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

@celery.task
def openai_response_task(ecli_id, extracted_text):
    logging.info(f"Sending data to OpenAI for ECLI ID: {ecli_id}")
    response_content = get_openai_response(ecli_id, extracted_text)
    logging.info(f"Received response from OpenAI for ECLI ID: {ecli_id}")
    return response_content

@celery.task
def error_handler(uuid):
    logging.info(f'Task {uuid} raised exception!')
