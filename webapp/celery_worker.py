from celery import Celery
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

def make_celery(app_name, redis_uri):
    celery = Celery(app_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Adjust according to your Redis SSL settings
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

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # Assuming app_context is defined if you need to use Flask context
            return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create and configure a single Celery instance.
redis_uri = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
app_name = 'webapp'
celery = make_celery(app_name, redis_uri)

@celery.task
def scrape_case_task(ecli_id):
    metadata, extracted_text = scrape_case(ecli_id)
    # No record exists, proceed to scrape and then extract metadata and raw text
    metadata, extracted_text = scrape_case(ecli_id)  # Ensure scrape_case returns metadata and extracted_text
                
    # Parsing and converting dates
    datum_uitspraak = datetime.strptime(metadata.get('Datum uitspraak', '1900-01-01'), "%d-%m-%Y").date() if 'Datum uitspraak' in metadata else None
    datum_publicatie = datetime.strptime(metadata.get('Datum publicatie', '1900-01-01'), "%d-%m-%Y").date() if 'Datum publicatie' in metadata else None

    # Create a new record with the extracted information
    new_record = ScrapeRecord(
        ecli_id=ecli_id,
        instantie=metadata.get('Instantie', None),
        datum_uitspraak=datum_uitspraak,
        datum_publicatie=datum_publicatie,
        zaaknummer=metadata.get('Zaaknummer', None),
        formele_relaties=metadata.get('Formele relaties', None),
        rechtsgebieden=metadata.get('Rechtsgebieden', None),
        bijzondere_kenmerken=metadata.get('Bijzondere kenmerken', None),
        inhoudsindicatie=metadata.get('Inhoudsindicatie', None),
        vindplaatsen=metadata.get('Vindplaatsen', None),
        metadata_json=metadata,  # Storing the entire metadata as a JSON object
        raw_text=extracted_text
        )
                
    # Add the new record to the session and commit it to the database
    db.session.add(new_record)
    db.session.commit()
    return ecli_id

@celery.task
def openai_response_task(ecli_id):
    response_content = get_openai_response(ecli_id)
    return response_content

@celery.task
def error_handler(uuid):
    print(f'Task {uuid} raised exception!')
