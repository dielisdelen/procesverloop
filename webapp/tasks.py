from .celery_config import celery
from models import db, ScrapeRecord
from datetime import datetime
from flask import current_app
from case_extractor_static import scrape_case
from openai_integration import get_openai_response

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
