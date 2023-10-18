import logging
import os

import pandas as pd
from asana_sync.data import get_current_order_date_and_number, get_single_customer_orders
from asana_sync.haney_asana import AsanaHaney
from asana_sync.postgres import create_psql_engine, write_last_order_date

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv


if os.getenv("ENV") == "prod":
    load_dotenv("app/.env/.env.prod")
    logger.info("Loading prod env")
else:
    load_dotenv("app/.env/.env.dev")
    logger.info("Loading dev env")


if __name__ == "__main__":
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
            