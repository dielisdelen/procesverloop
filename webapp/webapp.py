from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from CaseExtractor import scrape_case
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        ecli_id = request.form.get('ecli_id', '')

        if action == 'extract':
            existing_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
            if existing_record:
                # Record exists, so directly go to the timeline
                return redirect(url_for('timeline', ecli_id=ecli_id))
            else:
                # No record exists, proceed to scrape
                extracted_text = scrape_case(ecli_id)
                new_record = ScrapeRecord(ecli_id=ecli_id, raw_text=extracted_text)
                db.session.add(new_record)
                db.session.commit()

                # After storing the scraped data, process it with OpenAI
                get_openai_response(ecli_id)
                return redirect(url_for('timeline', ecli_id=ecli_id))

    return render_template('index.html')

@app.route('/timeline')
def timeline():
    ecli_id = request.args.get('ecli_id', '')
    events = []

    response_record = OpenAIResponse.query.filter_by(ecli_id=ecli_id).first()
    if response_record:
        try:
            openai_response = json.loads(response_record.response_data)
            events = openai_response.get("Events", [])
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding OpenAI response: {str(e)}")
            events = []
    else:
            print("No OpenAI response found for provided ECLI ID.")
            events = []

    return render_template('timeline.html', events=events, ecli_id=ecli_id)

if __name__ == '__main__':
    app.run(debug=True)
