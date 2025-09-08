from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .common.logger import logger
from datetime import datetime
from dateutil.tz import tzlocal
import logging

logging.getLogger('apscheduler').setLevel(logging.WARNING)

scheduler = BackgroundScheduler()

def start():
    logger.debug('start scheduler')
    scheduler.add_job(_example_job, IntervalTrigger(seconds=1))
    scheduler.start()

def stop():
    logger.debug('stop scheduler')
    scheduler.shutdown()

def _example_job():
    logger.info('Example Job: ' + datetime.now(tzlocal()).isoformat())
