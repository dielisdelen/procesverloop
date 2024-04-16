from celery import Celery
from flask import current_app  # You will not use this directly, it's shown just for context
from case_extractor_static import scrape_case
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# check if Async is enabled
# USE_ASYNC = os.getenv('USE_ASYNC', 'false').lower() == 'true'

# Create a Celery instance as a global variable
# celery = Celery(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create and configure a single Celery instance.
redis_uri = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
celery = Celery(__name__, broker=redis_uri, backend=redis_uri)

def init_celery(app):
    # SSL options setup
    ssl_options = {
        'ssl_cert_reqs': 'required',  # Or change to 'optional' or 'none' based on your Redis SSL setup
    }

    # General Celery configuration
    celery.conf.update(
        broker_url=app.config['REDIS_URI'],
        result_backend=app.config['REDIS_URI'],
        broker_transport_options={
            'fanout_prefix': True,
            'fanout_patterns': True,
            'visibility_timeout': 3600
        },
        result_backend_transport_options={
            'visibility_timeout': 3600
        },
        broker_use_ssl=ssl_options,
        redis_backend_use_ssl=ssl_options,
        # Routing and queue name configuration to include a consistent hash tag
        task_default_queue='celery{my_app}',
        task_default_exchange='celery{my_app}',
        task_default_routing_key='celery{my_app}',
    )

    # Ensure that tasks are executed in the Flask application context
    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask

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
    return response_content
    pass

@celery.task
def error_handler(uuid):
    logging.info(f'Task {uuid} raised exception!')
    pass
