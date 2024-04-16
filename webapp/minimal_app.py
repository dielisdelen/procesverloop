from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['REDIS_URI'] = os.getenv('REDIS_URI', 'redis://localhost:6379/0')

def make_celery(app):
    redis_uri = app.config['REDIS_URI']
    celery = Celery(app.import_name, broker=redis_uri, backend=redis_uri)

    celery.conf.update({
        'broker_url': redis_uri,
        'result_backend': redis_uri
    })

    # Ensure that tasks are executed in the Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task
def add_together(a, b):
    return a + b

@app.route('/')
def hello():
    result = add_together.delay(23, 42)
    return f'Result: {result.get(timeout=10)}'

if __name__ == '__main__':
    app.run(debug=True)
