import pika, psycopg2, os

from extractor.utils.product_details import product_details

# estublish database connection to postgres
DB_CONN = psycopg2.connect(
    host=os.getenv("HOST", default="postgres"),
    database=os.getenv("DATABASE", default="postgres"),
    user=os.getenv("USER", default="postgres"),
    password=os.getenv("PASSWORD", default="postgres"),
    port=os.getenv("PORT", default=5432),
)
DB_CONN.autocommit = True

product_details(conn=DB_CONN)


# use 'localhost' for local development and 'rabbitmq' for docker
RMQ_CONN = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
