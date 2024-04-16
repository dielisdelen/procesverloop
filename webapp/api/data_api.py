from flask import Blueprint, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import OpenAIResponse, ScrapeRecord  # Update the import path as necessary

api_blueprint = Blueprint('data_api', __name__)

print("data_api called")

db = SQLAlchemy()

@api_blueprint.route('/get-data', methods=['GET'])
def get_data():
    ecli_id = request.args.get('ecli_id', default=None, type=str)
    if not ecli_id:
        return jsonify({'error': 'Missing ecli_id parameter'}), 400

    openai_response = OpenAIResponse.query.filter_by(ecli_id=ecli_id).first()
    scrape_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()

    if not openai_response or not scrape_record:
        return jsonify({'error': 'Data not found for provided ECLI ID'}), 404

    # Assuming `response_data` is already in JSON-compatible format
    try:
        response_data = openai_response.response_data if openai_response else None
        instantie = scrape_record.instantie if scrape_record else None

        data = {
            'openai_response': response_data,
            'instantie': instantie   
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Failed to process data'}), 500
