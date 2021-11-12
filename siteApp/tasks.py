from celery import shared_task
from celery.utils.log import get_task_logger
from siteApp.sync import DbSyncTask

logger = get_task_logger(__name__)


@shared_task
def db_sync_task():
    logger.info("Start db synchronization")
    DbSyncTask.run()
    logger.info("Finsish db synchronization")

