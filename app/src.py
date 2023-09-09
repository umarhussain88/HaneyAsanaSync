from haney_asana import AsanaHaney
from postgres import create_psql_engine, write_last_order_date
from data import get_single_customer_orders, get_current_order_date_and_number
import pandas as pd
import os
import logging

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)
logger = logging.getLogger(__name__)





if __name__ == "__main__":
    
    
    logger.info('Starting script')
    logger.info('Connecting to database')
    
    engine = create_psql_engine(
        pg_db=os.getenv("POSTGRES_DB"),
        pg_host=os.getenv("POSTGRES_HOST"),
        pg_port=os.getenv("POSTGRES_PORT"),
        pg_user=os.getenv("POSTGRES_USER"),
        pg_password=os.getenv("POSTGRES_PASSWORD"),
    )
    
    
    haney_asana_api = AsanaHaney(workspace_id='1205454697900007')
    haney_asana_api.test_asana_api()
    
    df = get_single_customer_orders(engine)
    
    
    logger.info(df.shape)
    
    for row in df.itertuples(index=None):
        
        customer_note = haney_asana_api.create_customer_note('1205454651907136', row)
        
        api_response = haney_asana_api.create_customer_task(body=customer_note)
        
        task_gid = haney_asana_api.get_new_task_gid(api_response)
        logger.info(f'New task gid: {task_gid}')
        
        logger.info('moving task to notes section')
        haney_asana_api.move_task_to_section(task_gid=task_gid)
        
        
