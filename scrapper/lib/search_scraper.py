from selenium import webdriver
from selenium.webdriver.common.by import By
import json

from scrapper import RMQ_CONN, DB_CONN


class SearchScraper:
    def __init__(self):
        self.channel = self.setup_rabbitmq()
        print("SearchScraper initialized")

    def extractor_comm(self, data):
        self.channel.basic_publish(
            exchange="", routing_key="search2extractor", body=json.dumps(data)
        )

    def init_scrapper(self):
        self.extractor_comm({"message": "ping"})
        self.channel.basic_consume(
            queue="extractor2search",
            on_message_callback=self.process_status,
            auto_ack=True,
        )
        self.channel.start_consuming()

    def process_status(self, channel, method, properties, body):
        message_body = json.loads(body.decode())
        print(message_body)
        if message_body["message"] in ["pong", "reset"]:
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
        for item in url_data:
            try:
                cursor = DB_CONN.cursor()
                cursor.execute(
                    "INSERT INTO scraped_urls (query, url) VALUES (%s, %s)",
                    (item["query"], item["url"]),
                )
                DB_CONN.commit()
                cursor.close()
            except Exception:
                pass

    def log_data(self, search_query, data):
        with open(f"scraped_links_for_{search_query}.json", "w") as f:
            json.dump(data, f)

    def search_and_scrape(self):
        search_query = input("Enter product name: ")
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
        self.extractor_comm({"message": "start", "query": query})
