import pandas as pd
import logging
from sqlalchemy.exc import SQLAlchemyError





fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_single_customer_orders(engine):
    try:
        df = pd.read_sql("SELECT * FROM dm_shopify.single_customer_orders", con=engine)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving data from database {e}")
    return df


def get_current_order_date_and_number(data_frame: pd.Series) -> tuple:
    return data_frame[["order_number", "order_date"]].items(index=None)


