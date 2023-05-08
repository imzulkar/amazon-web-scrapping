from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
from scrapper import RMQ_CONN, DB_CONN
import logging

logging.getLogger(__name__) 

class SearchScraper:
    def __init__(self):
        self.channel = self.setup_rabbitmq()
        logging.info("SearchScraper initialized")
        
        try:
            self.products = os.environ['QUERY_PRODUCTS'].split(',')
        except KeyError:
            self.products = None

    def extractor_comm(self, data):
        self.channel.basic_publish(
            exchange="", routing_key="search2extractor", body=json.dumps(data)
        )

    def init_scrapper(self):
        self.extractor_comm({"action": "ping"})
        self.channel.basic_consume(
            queue="extractor2search",
            on_message_callback=self.process_status,
            auto_ack=True,
        )
        self.channel.start_consuming()

    def process_status(self, channel, method, properties, body):
        message_body = json.loads(body.decode())
        logging.info(message_body)
        if message_body["action"] in ["pong", "reset"]:
            # if self.products:
            #     query = self.products.pop()
            # else:
            #     query= input("Enter product name: ")
            self.search_and_scrape()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(options=options)

    def setup_rabbitmq(self):
        channel = RMQ_CONN.channel()
        channel.queue_declare(queue="extractor2search")
        channel.queue_declare(queue="search2extractor")
        return channel

    def store_data_in_database(self, url_data):
        cursor = DB_CONN.cursor()
        for item in url_data:
            try:
                cursor.execute(
                    "INSERT INTO scraped_urls (query, url) VALUES (%s, %s)",
                    (item["query"], item["url"]),
                )
            except Exception:
                pass
        # DB_CONN.commit()
        cursor.close()

    def log_data(self, search_query, data):
        with open(f"logs/products_url/scraped_links_for_{search_query}.json", "w") as f:
            json.dump(data, f)

    def search_and_scrape(self):
        try:
            search_query = self.products.pop() if self.products else input("Enter product name: ")
        except Exception as e:
            search_query = ''
            logging.warn("No more products to scrape")
        driver = self.setup_driver()
        driver.get(f"https://www.amazon.com/s?k={search_query}")
        
        product_links = driver.find_elements(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
       

        product_data = []
        query = search_query.replace(" ", "_")

        for link in product_links[:5]:
            product_url = link.get_attribute("href")
            product_data.append({"query": query, "url": product_url})

        driver.quit()

        self.store_data_in_database(product_data)
        self.log_data(search_query=query, data=product_data)
        self.extractor_comm({"action": "start", "query": query})
