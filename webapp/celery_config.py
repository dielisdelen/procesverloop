from celery import Celery

def make_celery(app):
    redis_uri = app.config['REDIS_PROD_URI']
    celery = Celery(app.import_name, broker=redis_uri, backend=redis_uri)

    ssl_options = {
        'ssl_cert_reqs': 'required',  # Change to 'optional' or 'none' as per your Redis setup
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
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

@celery.task
def add_together(a, b):
    print(f'Adding {a} + {b}')
    return a + b
