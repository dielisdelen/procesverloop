# procesverloop

## Overview
Webapplication for sending ECLI's to ChatGPT to get a short but precise summary of facts in a timeline form.

## Prerequisites
- Python 3.8+
- Virtualenv

## Setup
1. Clone the repository and navigate into it:

git clone https://github.com/dielisdelen/procesverloop.git
cd procesverloop

2. Set up a virtual environment and activate it:

python3 -m venv venv
source venv/bin/activate

3. Install dependencies:

pip install -r requirements.txt

4. Run the application:

export FLASK_APP=app.py
export FLASK_ENV=development
flask run




## Steps for Diel

1. Navigate to the directory patroonlabs/procesverloop
2. Start virtual environment: source venv/bin/activate
3. move to directory: webapp
4. start script: python3 webapp.py
5. open browser with this address: http://127.0.0.1:5000
6. Primary ECLI for MVP: ECLI:NL:RBMNE:2023:4481

For web Flask, same but then this command: flask run --host=0.0.0.0
