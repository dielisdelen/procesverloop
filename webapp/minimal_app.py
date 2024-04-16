from flask import Flask
from celery_config import celery, add_together
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['REDIS_PROD_URI'] = os.getenv('REDIS_PROD_URI')

@app.route('/')
def hello():
    result = add_together.delay(23, 42)
    return 'Task submitted! Check your worker console for the result.'

if __name__ == '__main__':
    app.run(debug=True)
