# celery_config.py
from celery import Celery
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_celery(app_name, redis_uri):
    logger.info("Initializing Celery for app: %s", app_name)
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

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # Assuming app_context is defined if you need to use Flask context
            return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

redis_uri = os.getenv('REDIS_PROD_URI')
app_name = 'webapp_new'
celery = make_celery(app_name, redis_uri)

celery.autodiscover_tasks(['webapp'])