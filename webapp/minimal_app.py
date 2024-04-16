# minimal_app.py
from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config['REDIS_URI'] = 'rediss://pvredis-a42qr8.serverless.eun1.cache.amazonaws.com:6379'

def make_celery(app):
    redis_uri = app.config['REDIS_URI']
    celery = Celery(app.import_name, broker=redis_uri, backend=redis_uri)

    # Additional SSL parameters for secure Redis connection
    ssl_options = {
        'ssl_cert_reqs': 'required',  # Change to 'optional' or 'none' as per your Redis setup and security requirements
    }
    
    # Update Redis URL with additional SSL options
    celery.conf.update(
        broker_use_ssl=ssl_options,
        redis_backend_use_ssl=ssl_options
    )

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
