# celery_config.py
from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def make_celery(app_name):
    redis_uri = os.getenv('REDIS_PROD_URI')
    celery = Celery(app_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Adjust according to your Redis SSL settings
    }

    celery.conf.update({
        'broker_url': redis_uri,
        'result_backend': redis_uri,
        'broker_use_ssl': ssl_options,
        'redis_backend_use_ssl': ssl_options,
    })

    return celery

app_name = 'webapp_new'  # Use a meaningful name
celery = make_celery(app_name)
