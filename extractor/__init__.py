import logging
import pika
import psycopg2

from extractor.utils.product_details import product_details


LOGGER = logging.getLogger(__name__)

DB_CONN = psycopg2.connect(
    host="localhost",
    database="products_scrapper",
    user="postgres",
    password="7874",
    port=5432,
)

DB_CONN.autocommit = True

product_details(conn=DB_CONN)


RMQ_CONN = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
