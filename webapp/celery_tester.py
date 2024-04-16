from flask import Flask
from celery import Celery

app = 'webapp'

redis_uri = 'rediss://pvredis-a42qr8.serverless.eun1.cache.amazonaws.com:6379'

celery = Celery(app.name, broker=redis_uri)