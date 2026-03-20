import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("wateen")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# Set beat schedule directly on app config
app.conf.beat_schedule = {
    "flush-nurse-locations": {
        "task": "visits.tasks.flush_nurse_locations",
        "schedule": 60.0,
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
