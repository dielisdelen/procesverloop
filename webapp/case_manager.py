from flask import Flask, request, redirect, url_for, render_template
from controllers import process_extraction
from models import db
from api.data_api import data_api

from dotenv import load_dotenv
import os

import logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config.from_object('config.DevelopmentConfig')
app.register_blueprint(data_api, url_prefix='/api')

db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    ecli_id = request.form.get('ecli_id', '')
    result = process_extraction(ecli_id)
    if result:
        return redirect(url_for('timeline', ecli_id=ecli_id))
    else:
        return "Error processing the ECLI ID", 400

@app.route('/timeline')
def timeline():
    ecli_id = request.args.get('ecli_id', '')
    return render_template('timeline.html', ecli_id=ecli_id)

@app.route('/over')
def about_page():
    return render_template('about.html')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
