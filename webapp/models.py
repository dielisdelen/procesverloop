from quart import Quart
from quart_sqlalchemy import SQLAlchemyConfig
from quart_sqlalchemy import SQLAlchemy
from quart_sqlalchemy.framework import QuartSQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

def get_scrape_record_class():
    from webapp import db
    class ScrapeRecord(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ecli_id = db.Column(db.String(255), unique=True, nullable=False)
        raw_text = db.Column(db.Text, nullable=False)
        scrape_date = db.Column(db.DateTime, default=db.func.current_timestamp())
        instantie = db.Column(db.String, nullable=True)  # Court or Instance
        datum_uitspraak = db.Column(db.Date, nullable=True)  # Date of Verdict
        datum_publicatie = db.Column(db.Date, nullable=True)  # Date of Publication
        zaaknummer = db.Column(db.String, nullable=True)  # Case Number
        formele_relaties = db.Column(db.Text, nullable=True)  # Formal Relations
        rechtsgebieden = db.Column(db.String, nullable=True)  # Legal Areas
        bijzondere_kenmerken = db.Column(db.String, nullable=True)  # Special Features
        inhoudsindicatie = db.Column(db.Text, nullable=True)  # Content Indication
        vindplaatsen = db.Column(db.String, nullable=True)  # Locations Found
        metadata_json = db.Column(db.JSON, nullable=True)  # Additional Metadata in JSON format
    return ScrapeRecord

def get_openai_response_async_class():
    from webapp import db
    class OpenAIResponse(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ecli_id = db.Column(db.String(255), db.ForeignKey('scrape_record.ecli_id'), unique=True)
        response_data = db.Column(JSONB, nullable=False)
        response_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    return OpenAIResponse
