from flask import Flask, request, render_template, session, redirect, url_for
from flask_session import Session
from CaseExtractor import scrape_case
from openai_integration import get_openai_response
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234567890"  # Necessary for session encryption
app.config["SESSION_TYPE"] = "filesystem"  # Stores session data on the filesystem
Session(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ""
    case_number = ""
    openai_response = ""

    if request.method == 'POST':
        action = request.form.get('action')
        case_number = request.form.get('case_number', '')

        if action == 'extract':
            # Call your scraping function
            extracted_text = scrape_case(case_number)
        elif action == 'send_to_openai':
            print("Sending to OpenAI...")
            extracted_text = request.form.get('extracted_text', '')
            print(f"Extracted Text: {extracted_text}")
            openai_response = get_openai_response(extracted_text)
            print(f"OpenAI Response: {openai_response}")
            session['openai_response'] = openai_response
            return redirect(url_for('timeline')) 
    
    return render_template('index.html', case_number=case_number, extracted_text=extracted_text, openai_response=openai_response)

@app.route('/timeline')
def timeline():
    openai_response = session.get('openai_response', '{}')
    events = json.loads(openai_response).get("Events", [])

    return render_template('timeline.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)
