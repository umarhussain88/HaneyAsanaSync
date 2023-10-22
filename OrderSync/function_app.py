import azure.functions as func
import logging
import os
from asana_sync.haney_asana import AsanaHaney
import sentry_sdk
from sentry_sdk.integrations.serverless import serverless_function


sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )


app = func.FunctionApp()
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.timer_trigger(schedule="0 * * */1 *", arg_name="OrderTimer", run_on_startup=False,
              use_monitor=False) 
def emailordertimer(OrderTimer: func.TimerRequest) -> None:
    
    if OrderTimer.past_due:
        logger.info('The timer is past due!')

    logger.info("Starting script")

    haney_asana_api = AsanaHaney(
        workspace_id=os.getenv("HANEY_WORKSPACE_ID"),
        access_token=os.getenv("ASANA_TOKEN"),
        notes_section_gid=os.getenv("NOTES_SECTION_GID"),
        admin_assignee_section_gid=os.getenv("NOTES_USER_ID"),
        admin_order_entry_section_gid=os.getenv("ADMIN_ORDER_ENTRY_SECTION_GID"),
    )

    haney_asana_api.test_asana_api()

    section_tasks = haney_asana_api.get_section_tasks_since_date(section_gid=haney_asana_api.admin_order_entry_section_gid)
    
    if section_tasks:
        for item in section_tasks:
            haney_asana_api.assign_incomplete_task(item.to_dict().get('gid'))
    
    logging.info('Python timer trigger function executed.')