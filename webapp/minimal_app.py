from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config['REDIS_URI'] = 'pvredissingle.a42qr8.ng.0001.eun1.cache.amazonaws.com:6379'

def make_celery(app):
    redis_uri = app.config['REDIS_URI']
    celery = Celery(app.import_name, broker=redis_uri, backend=redis_uri)

    # Additional SSL parameters for secure Redis connection
    ssl_options = {
        'ssl_cert_reqs': 'required'  # Change to 'optional' or 'none' as per your Redis setup and security requirements
    }
    
    # Update Redis URL with additional SSL options and configure key prefix with hash tags
    celery.conf.update(
        broker_use_ssl=ssl_options,
        redis_backend_use_ssl=ssl_options,
        task_default_queue='celery#{my_app}',
        task_default_exchange='celery#{my_app}',
        task_default_routing_key='celery#{my_app}',
    )

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
