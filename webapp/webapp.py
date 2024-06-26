from flask import Flask, request, render_template, redirect, url_for, make_response
from dotenv import load_dotenv

#Scraping imports
from case_extractor_static import scrape_case

#Database imports

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from openai_integration import get_openai_response
from models import db, ScrapeRecord, OpenAIResponse

# API Imports
from api.data_api import api_blueprint

#Limiter imports
from limiter_setup import init_limiter

# General imports
import json
import os
import time

# Load environment variables
load_dotenv()

# Check if Redis Limiter is enabled
USE_REDIS_LIMITER = os.getenv('USE_REDIS_LIMITER', 'false').lower() == 'true'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(api_blueprint, url_prefix='/api')

db.init_app(app)

if USE_REDIS_LIMITER:
    limiter = init_limiter(app)
else:
    # Define a dummy limiter decorator that does nothing
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    limiter = DummyLimiter()

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")
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
                time.sleep(1)

                # After storing the scraped data, process it with OpenAI
                get_openai_response(ecli_id)
                return redirect(url_for('timeline', ecli_id=ecli_id))

        pass

    return render_template('index.html')

@app.route('/timeline')
def timeline():
    ecli_id = request.args.get('ecli_id', '')
    # Now just passing ecli_id to the template, no events
    return render_template('timeline.html', ecli_id=ecli_id)

@app.route('/over')
def new_page():
    return render_template('over.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/aanmelden')
def aanmelden():
    return render_template('aanmelden.html')    

@app.route('/profiel')
def profiel():
    return render_template('profiel.html')   

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
