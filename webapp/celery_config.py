# celery_config.py
from celery import Celery
import os
from dotenv import load_dotenv
import logging
from models import db, ScrapeRecord
from datetime import datetime
from flask import current_app
from case_extractor_static import scrape_case
from openai_integration import get_openai_response

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_celery(app_name, redis_uri):
    logger.info("Initializing Celery for app: %s", app_name)
    celery = Celery(app_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Adjust according to your Redis SSL settings
    }

    celery.conf.update({
        'broker_url': redis_uri,
        'result_backend': redis_uri,
        'broker_use_ssl': ssl_options,
        'redis_backend_use_ssl': ssl_options,
    })

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # Assuming app_context is defined if you need to use Flask context
            return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

redis_uri = os.getenv('REDIS_PROD_URI')
app_name = 'webapp_new'
celery = make_celery(app_name, redis_uri)

@celery.task
def scrape_case_task(ecli_id):
    with current_app.app_context():
        metadata, extracted_text = scrape_case(ecli_id)
        datum_uitspraak = datetime.strptime(metadata.get('Datum uitspraak', '1900-01-01'), "%Y-%m-%d").date() if 'Datum uitspraak' in metadata else None
        datum_publicatie = datetime.strptime(metadata.get('Datum publicatie', '1900-01-01'), "%Y-%m-%d").date() if 'Datum publicatie' in metadata else None

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
            metadata_json=metadata,
            raw_text=extracted_text
        )
        
        db.session.add(new_record)
        db.session.commit()
        return ecli_id
    pass

@celery.task
def openai_response_task(ecli_id):
    with current_app.app_context():
        response_content = get_openai_response(ecli_id)
        return response_content
    pass

@celery.task
def error_handler(uuid):
    print(f'Task {uuid} raised exception!')
    pass