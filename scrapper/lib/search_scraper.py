from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
from scrapper import RMQ_CONN, DB_CONN
import logging


class SearchScraper:
    def __init__(self):
        self.channel = self.setup_rabbitmq()  # setup rabbitmq connection
        print("SearchScraper initialized")
        self.products = os.getenv(
            "QUERY_PRODUCTS", default=None
        )  # get products from environment variable
        self.products = self.products.split(",") if self.products else None

        self.init_scrapper()  # start scrapper

    def extractor_comm(self, data):
        # exreactor to scrapper communication channel
        self.channel.basic_publish(
            exchange="", routing_key="search2extractor", body=json.dumps(data)
        )

    def init_scrapper(self):
        self.extractor_comm({"action": "ping"})  # send ping to message extractor
        self.channel.basic_consume(
            queue="extractor2search",
            on_message_callback=self.process_status,
            auto_ack=True,
        )
        self.channel.start_consuming()  # start consuming messages from extractor

    def process_status(self, channel, method, properties, body):
        # check extractor status and start scrapper
        message_body = json.loads(body.decode())
        print(message_body)
        if message_body["action"] in ["pong", "reset"]:
            self.search_and_scrape()

    def setup_driver(self):
        # selenium driver setup for chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(options=options)

    def setup_rabbitmq(self):
        # rabbitmq connection setup
        channel = RMQ_CONN.channel()
        channel.queue_declare(queue="extractor2search")
        channel.queue_declare(queue="search2extractor")
        return channel

    def store_data_in_database(self, url_data):
        # store data in database
        cursor = DB_CONN.cursor()
        for item in url_data:
            try:
                cursor.execute(
                    "INSERT INTO scraped_urls (query, url) VALUES (%s, %s)",
                    (item["query"], item["url"]),
                )
            except Exception:
                pass
        cursor.close()

    def log_data(self, search_query, data):
        # log data stored in json file
        with open(f"logs/products_url/scraped_links_for_{search_query}.json", "w") as f:
            json.dump(data, f)

    def search_and_scrape(self):
        # search and scrape products
        try:
            search_query = (
                self.products.pop() if self.products else input("Enter product name: ")
            )
        except Exception as e:
            search_query = ""
            logging.warning("No more products to scrape")
        print(search_query)
        driver = self.setup_driver()
        driver.get(f"https://www.amazon.com/s?k={search_query}")

        product_links = driver.find_elements(
            By.XPATH,
            './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]',
        )

        product_data = []
        query = search_query.replace(" ", "_")

        for link in product_links[:5]:
            product_url = link.get_attribute("href")
            product_data.append({"query": query, "url": product_url})

        driver.quit()

        self.store_data_in_database(product_data)  # store data in database
        self.log_data(
            search_query=query, data=product_data
        )  # log data stored in json file
        self.extractor_comm(
            {"action": "start", "query": query}
        )  # send start message to extractor
