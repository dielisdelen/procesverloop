from models import db, ScrapeRecord

def get_scraped_data(ecli_id):
    record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
    if record:
        return record.raw_text
    else:
        return None

# You can add more database-related functions here (e.g., storing OpenAI responses)
