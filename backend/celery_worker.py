from app import create_app
from celery_utils import make_celery

app = create_app()
celery = make_celery(app)

# Ensure tasks are registered
import tasks
