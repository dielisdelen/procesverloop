# procesverloop

## Overview
Webapplication for sending ECLI's to ChatGPT to get a short but precise summary of facts in a timeline form.

## Prerequisites
- Python 3.8+
- Virtualenv

For python use: 
```sh
brew install python
```
For vitualenv use:
```sh
pip install virtualenv
```
## Setup
1. Navigate to directory where you want to clone the repository

2. Clone the repository and navigate into it:

```sh
git clone https://github.com/dielisdelen/procesverloop.git
cd procesverloop
```

3. Set up a virtual environment and activate it:
```sh
python3 -m venv venv
source venv/bin/activate
```
4. Install dependencies:
```sh
pip install -r requirements.txt
```
5. Run the application:
```sh
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```



## Steps for Diel

1. Navigate to the directory patroonlabs/procesverloop
2. Start virtual environment: source venv/bin/activate
3. move to directory: webapp
4. start script: python3 webapp.py
5. open browser with this address: http://127.0.0.1:5000
6. Primary ECLI for MVP: ECLI:NL:RBMNE:2023:4481

For web Flask, same but then this command: flask run --host=0.0.0.0