from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery(app_name, redis_uri):
    celery = Celery(app_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Adjust according to your Redis SSL settings
    }

    celery.conf.update({
        'broker_url': redis_uri,
        'result_backend': redis_uri,
        'broker_use_ssl': ssl_options,
        'redis_backend_use_ssl': ssl_options,
        'task_default_queue': 'celery{my_app}',
        'task_default_exchange': 'celery{my_app}',
        'task_default_routing_key': 'celery{my_app}',
    })

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # Assuming app_context is defined if you need to use Flask context
            return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

redis_uri = os.getenv('REDIS_PROD_URI')
app_name = 'minimal_app'
celery = make_celery(app_name, redis_uri)

@celery.task
def add_together(a, b):
    print(f'Adding {a} + {b}')
    return a + b
