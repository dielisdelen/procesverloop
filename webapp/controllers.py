from models import ScrapeRecord, db
from case_extractor_static import scrape_case
from openai_integration import get_openai_response
from datetime import datetime

def process_extraction(ecli_id):
    existing_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
    if existing_record:
        return existing_record
    else:
        metadata, extracted_text = scrape_case(ecli_id)
        if metadata and extracted_text:
            return create_scrape_record(ecli_id, metadata, extracted_text)
        else:
            return None
    pass

def create_scrape_record(ecli_id, metadata, extracted_text):
    datum_uitspraak = datetime.strptime(metadata.get('Datum uitspraak', '1900-01-01'), "%d-%m-%Y").date() if 'Datum uitspraak' in metadata else None
    datum_publicatie = datetime.strptime(metadata.get('Datum publicatie', '1900-01-01'), "%d-%m-%Y").date() if 'Datum publicatie' in metadata else None

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
    print("Data added:", new_record)
    get_openai_response(ecli_id)
    return new_record
    pass
