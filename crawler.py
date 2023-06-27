import os

# from worker import app
from celery import Celery
from celery.schedules import crontab
from dotenv.main import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapers.scrapers.spiders.kohls import KohlSpider
# scrapers.scrapers.spiders.wal
from scrapers.scrapers.spiders.walmart import WalmartSpider
from scrapers.scrapers.spiders.target import TargetSpider

# load in and assign environment variables for use``
load_dotenv()
broker_url = os.environ['CELERY_BROKER_URL']
backend_url = os.environ["CELERY_BACKEND_URL"]

app = Celery(
    __name__,
    broker=broker_url,
    backend=backend_url
)
settings = get_project_settings()

process = CrawlerProcess(settings)

app.conf.beat_schedule = {
    'crawl-walmart': {
        'task': 'tasks.crawl_walmart',
        'schedule': 120,
    },
    'crawl-kohls': {
        'task': 'tasks.crawl_kohls',
        'schedule': 1800,
    },
    'crawl-target': {
        'task': 'tasks.crawl_kohls',
        'schedule': 30
    }
}


@app.task(name='tasks.crawl_walmart')
def crawl_walmart():
    process.crawl(WalmartSpider)
    process.start(stop_after_crawl=True)
    # time.sleep(3600)
    # proc.stop()


@app.task(name='tasks.crawl_kohls')
def crawl_kohls():
    # process = CrawlerProcess(settings)
    process.crawl(KohlSpider)
    process.start(stop_after_crawl=True)

@app.task(name='tasks.crawl_target')
def crawl_target():
    process.crawl(TargetSpider)
    process.start(stop_after_crawl=True)

# if __name__=="__main__":
#     crawl_kohls.delay()