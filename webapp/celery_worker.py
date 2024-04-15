from celery import Celery
from flask import current_app  # You will not use this directly, it's shown just for context
from case_extractor_static import scrape_case
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse
from datetime import datetime
import os

# Create a Celery instance as a global variable
celery = Celery(__name__)

def make_celery(flask_app):
    # Configure the global celery instance with Flask app settings
    celery.main = flask_app.import_name
    celery.conf.update(
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    
    # Ensure that tasks are executed in the flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)
                
    celery.Task = ContextTask

    return celery  # This returns the configured global instance

@celery.task
def scrape_case_task(ecli_id):
    metadata, extracted_text = scrape_case(ecli_id)
    if extracted_text != "Error during navigation or data retrieval." and extracted_text != "Error during parsing.":
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
    print(f'Task {uuid} raised exception!')
