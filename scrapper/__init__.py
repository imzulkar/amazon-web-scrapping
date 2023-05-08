import logging
import pika
import psycopg2

from scrapper.utils.init_db_table import init_urls_table


LOGGER = logging.getLogger(__name__)
DB_CONN = psycopg2.connect(
    host="localhost",
    database="products_scrapper",
    user="postgres",
    password="7874",
    port=5432,
)
# DB_CONN = psycopg2.connect(
#     host="postgres",
#     database="postgres",
#     user="postgres",
#     password="postgres",
#     port=5432,
# )


DB_CONN.autocommit = True


init_urls_table(conn=DB_CONN)


RMQ_CONN = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
