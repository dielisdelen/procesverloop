from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['REDIS_PROD_URI'] = os.getenv('REDIS_PROD_URI')

# Import the Celery configuration and task from a separate module
from celery_config import make_celery, add_together

celery = make_celery(app)

@app.route('/')
def hello():
    result = add_together.delay(23, 42)
    # Asynchronously fetching the result may not be suitable for all real-time applications
    return 'Task submitted! Check your worker console for the result.'

if __name__ == '__main__':
    app.run(debug=True)
