import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanna_backend.settings')

app = Celery('tanna_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'check-expired-payments': {
        'task': 'payments.tasks.check_expired_payments',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-webhooks': {
        'task': 'payments.tasks.cleanup_old_payment_webhooks',
        'schedule': 86400.0,  # Every 24 hours
    },
}