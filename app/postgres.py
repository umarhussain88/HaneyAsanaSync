from sqlalchemy import create_engine



def create_psql_engine(pg_host, pg_port, pg_user, pg_password, pg_db):
    """Creates a SQLAlchemy engine for the Postgres database."""
    engine =  create_engine(
        f'postgresql://{pg_user}:{pg_password}'
        f'@{pg_host}:{pg_port}/{pg_db}'
    )
    
    return engine

def write_last_order_date(engine : create_engine, order_date : str, order_number : str) -> None:
    """Writes the last order date to the database."""
    engine.execute(f"INSERT INTO dm_shopify.last_order_date(order_number, order_date) VALUES ('{order_number}', '{order_date}')")
    
    
    