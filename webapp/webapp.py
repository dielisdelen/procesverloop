from flask import Flask, request, render_template, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from CaseExtractor import scrape_case
from openai_integration import get_openai_response
import json
from data_manager import get_scraped_data

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234567890"  # Necessary for session encryption
app.config["SESSION_TYPE"] = "filesystem"  # Stores session data on the filesystem
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pvpostgres:rx0FPhDNRVyaANczkE7W@pv-database-postgresql.c1uq82i0e5yr.eu-north-1.rds.amazonaws.com/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)

from models import db, ScrapeRecord, OpenAIResponse
db.init_app(app)

# Make sure to move `db.create_all()` into a place where it is executed once,
# such as within an application context in `webapp.py` if necessary
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ""
    ecli_id = ""
    openai_response = ""

    if request.method == 'POST':
        action = request.form.get('action')
        ecli_id = request.form.get('ecli_id', '')  # Updated from case_number to ecli_id

        if action == 'extract':
            # Call your scraping function
            extracted_text = scrape_case(ecli_id)  # Updated argument to ecli_id
            new_record = ScrapeRecord(ecli_id=ecli_id, raw_text=extracted_text)
            db.session.add(new_record)
            db.session.commit()
        elif action == 'send_to_openai':
            ecli_id = request.form.get('ecli_id', '')
            extracted_text = get_scraped_data(ecli_id)  # Retrieve stored data
            if extracted_text:
                openai_response = get_openai_response(extracted_text)
                print("OpenAI response received:", openai_response)
                
                # Check if an OpenAI response already exists for this ECLI ID
                existing_response = OpenAIResponse.query.filter_by(ecli_id=ecli_id).first()
                if existing_response:
                    # Update the existing record
                    existing_response.response_data = openai_response
                    existing_response.response_date = db.func.current_timestamp()
                else:
                    # No existing response, so create a new record
                    new_response_record = OpenAIResponse(ecli_id=ecli_id, response_data=openai_response)
                    db.session.add(new_response_record)
                
                db.session.commit()
                print("OpenAI response stored in the database")

                #session['openai_response'] = openai_response  # Consider database storage over session
                return redirect(url_for('timeline', ecli_id=ecli_id))
            else:
                #session['openai_response'] = "No data found for provided ECLI ID."
                return redirect(url_for('index'))

    
    return render_template('index.html', ecli_id=ecli_id, extracted_text=extracted_text, openai_response=openai_response)

@app.route('/timeline')
def timeline():
    ecli_id = request.args.get('ecli_id', '')
    if ecli_id:
        response_record = OpenAIResponse.query.filter_by(ecli_id=ecli_id).first()
        if response_record:
            openai_response = response_record.response_data
            try:
                print("OpenAI Response:", openai_response)
                events = json.loads(openai_response).get("Events", [])
            except json.decoder.JSONDecodeError:
                events = []
                print("Failed to decode JSON from OpenAI response.")
        else:
            openai_response = "No OpenAI response found for provided ECLI ID."
            events = []  # Ensure events is defined even if no response was found
    else:
        openai_response = "No ECLI ID provided."
        events = []  # Ensure events is defined even if no ECLI ID is provided

    # Render the timeline template, passing the events for display
    return render_template('timeline.html', events=events)


if __name__ == '__main__':
    app.run(debug=True)
