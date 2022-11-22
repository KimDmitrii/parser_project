from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parser.settings')
app = Celery('parser')
app.conf.timezone = 'UTC'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'scrapping-task-every-15-minutes': {
        'task': 'scraping.tasks.getLinksFromPagination',
        'schedule': crontab(minute='*/15'),
    },
}
