from celery import Celery
from flask import current_app
from case_extractor_static import scrape_case
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse
from datetime import datetime
import os

def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(flask_app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(current_app)

@celery.task
def scrape_case_task(ecli_id):
    # Call the scraping function
    metadata, extracted_text = scrape_case(ecli_id)
    
    # Process the results (e.g., saving to the database)
    if extracted_text != "Error during navigation or data retrieval." and extracted_text != "Error during parsing.":
        # Parsing and converting dates, creating database records, etc.
        # Assume that datetime parsing and record creation happens here
        new_record = ScrapeRecord(metadata=metadata, raw_text=extracted_text)
        db.session.add(new_record)
        db.session.commit()

    return ecli_id, extracted_text

@celery.task
def openai_response_task(ecli_id, extracted_text):
    response_content = get_openai_response(ecli_id, extracted_text)
    return response_content

@celery.task
def error_handler(uuid):
    # Handle error scenario
    print(f'Task {uuid} raised exception!')