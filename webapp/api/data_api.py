from flask import Blueprint, jsonify, request, current_app
from models import db, ScrapeRecord, OpenAIResponse
import logging
logging.basicConfig(level=logging.DEBUG)

# Create a Blueprint for data-related operations
data_api = Blueprint('data_api', __name__)

def record_to_dict(record):
    """Converts a database model instance into a dictionary."""
    if isinstance(record, ScrapeRecord):
        return {
            'ecli_id': record.ecli_id,
            'raw_text': record.raw_text,
            'instantie': record.instantie,
            'datum_uitspraak': record.datum_uitspraak.isoformat() if record.datum_uitspraak else None,
            'datum_publicatie': record.datum_publicatie.isoformat() if record.datum_publicatie else None,
            'zaaknummer': record.zaaknummer,
            'formele_relaties': record.formele_relaties,
            'rechtsgebieden': record.rechtsgebieden,
            'bijzondere_kenmerken': record.bijzondere_kenmerken,
            'inhoudsindicatie': record.inhoudsindicatie,
            'vindplaatsen': record.vindplaatsen
        }
    elif isinstance(record, OpenAIResponse):
        return {
            'ecli_id': record.ecli_id,
            'response_data': record.response_data
        }
    return None

@data_api.route('/get-data', methods=['GET'])
def api_get_data():
    logging.debug(f"hey")
    ecli_id = request.args.get('ecli_id')
    logging.debug(f"Received ecli_id: {ecli_id}")
    if not ecli_id:
        return jsonify({'error': 'Missing ecli_id parameter'}), 400

    try:
        scrape_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
        openai_response = OpenAIResponse.query.filter_by(ecli_id=ecli_id).first()

        if not scrape_record:
            return jsonify({'error': 'No ScrapeRecord found'}), 404
        if not openai_response:
            return jsonify({'error': 'No OpenAIResponse found'}), 404

        scrape_data = record_to_dict(scrape_record)
        openai_data = record_to_dict(openai_response)

        return jsonify({
            'scrape_data': scrape_data,
            'openai_data': openai_data
        })
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve data: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

# Register this Blueprint in your main application instance
# Example: app.register_blueprint(data_api, url_prefix='/api')
