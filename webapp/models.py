from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ScrapeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ecli_id = db.Column(db.String(255), unique=True, nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    scrape_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class OpenAIResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ecli_id = db.Column(db.String(255), db.ForeignKey('scrape_record.ecli_id'), unique=True)
    response_data = db.Column(db.JSONB, nullable=False)
    response_date = db.Column(db.DateTime, default=db.func.current_timestamp())
