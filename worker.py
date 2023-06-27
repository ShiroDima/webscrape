from celery import Celery
from dotenv.main import load_dotenv
import os

# load in and assign environment variables for use
load_dotenv()
broker_url = os.environ['CELERY_BROKER_URL']
backend_url = os.environ["CELERY_BACKEND_URL"]

app = Celery("scraper_schedule")

print(broker_url)