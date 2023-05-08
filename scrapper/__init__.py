import pika, psycopg2, os

from scrapper.utils.init_db_table import init_urls_table

# estublish database connection to postgres
DB_CONN = psycopg2.connect(
    host=os.getenv("HOST", default="postgres"),
    database=os.getenv("DATABASE", default="postgres"),
    user=os.getenv("USER", default="postgres"),
    password=os.getenv("PASSWORD", default="postgres"),
    port=os.getenv("PORT", default=5432),
)


DB_CONN.autocommit = True


init_urls_table(conn=DB_CONN)  # create table if not exists


# use 'localhost' for local development and 'rabbitmq' for docker
RMQ_CONN = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)  # establish connection to rabbitmq for communication between two bots(scrapper and extractor)
