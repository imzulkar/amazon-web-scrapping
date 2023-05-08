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
)

init_urls_table(conn=DB_CONN)


RMQ_CONN = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
