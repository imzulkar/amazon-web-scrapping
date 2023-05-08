from selenium import webdriver
from selenium.webdriver.common.by import By
from extractor.__init__ import RMQ_CONN, DB_CONN
import json, logging


class Product:
    def __init__(self):
        self.channel = self.setup_rabbitmq()
        print("Product initialized")
        self.consume_status()  # start consuming messages from scrapper

    def scrapper_comm(self, data):
        # scrapper to extractor communication channel
        self.channel.basic_publish(
            exchange="", routing_key="extractor2search", body=json.dumps(data)
        )

    def consume_status(self):
        self.channel.basic_consume(
            queue="search2extractor",
            on_message_callback=self.process_status,
            auto_ack=True,
        )
        return self.channel.start_consuming()

    def process_status(self, channel, method, properties, body):
        # check scrapper status and start product scrapping
        message_body = json.loads(body.decode())
        print(message_body)
        if message_body["action"] == "ping":
            self.scrapper_comm({"action": "pong"})
        elif message_body["action"] == "start":
            self.process_product_scrapping_op(
                message_body["query"]
            )  # start product details scrapping
        else:
            pass

    def process_product_scrapping_op(self, search_query):
        # process product scrapping operation
        product_urls = self.get_urls_from_db(
            search_query
        )  # get product urls from database
        product_data = self.scrape_product(product_urls)  # scrape product details
        self.store_data_in_database(product_data)  # store product details in database
        self.log_data(search_query, product_data)  # log product details
        self.scrapper_comm(
            {"action": "reset"}
        )  # reset scrapper and send message to scrapper for new query

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
        # rabbitmq setup
        channel = RMQ_CONN.channel()
        channel.queue_declare(queue="extractor2search")
        channel.queue_declare(queue="search2extractor")
        return channel

    def get_urls_from_db(self, query):
        # get and return product urls from database
        cursor = DB_CONN.cursor()
        cursor.execute("SELECT url FROM scraped_urls WHERE query=%s", (query,))
        results = cursor.fetchall()
        urls = [row[0] for row in results]
        cursor.close()
        return urls

    def scrape_product(self, product_urls):
        # scrape product details from amazon
        driver = self.setup_driver()
        products = []
        for item in product_urls:
            driver.get(item)
            try:
                product_title = driver.find_element(
                    By.XPATH, "//span[@id='productTitle']"
                ).get_attribute("innerHTML")
            except Exception:
                product_title = "N/A"
            try:
                product_price = driver.find_element(
                    By.XPATH,
                    "//span[@class='a-price a-text-price a-size-medium apexPriceToPay']/span[@class='a-offscreen']",
                ).get_attribute("innerHTML")
            except Exception:
                product_price = "N/A"
            try:
                product_rating = (
                    driver.find_element(By.XPATH, "//span[@class='a-icon-alt']")
                    .get_attribute("innerHTML")
                    .split(" ")[0]
                )
            except Exception:
                product_rating = "N/A"

            # more product details can be added here and extracted from amazon, for testing purpose I have added only few details

            product = {
                "product_title": product_title.strip(),
                "product_price": product_price,
                "product_rating": product_rating,
                "product_url": item,
            }

            print(f"Scrapped for - {product_title.strip()}")
            products.append(
                product
            )  # append product details to products list for further processing

        driver.quit()

        return products

    def log_data(self, search_query, data):
        # log products details in json file
        with open(
            f"logs/products_detail/scraped_products_for_{search_query}.json", "w"
        ) as f:
            json.dump(data, f)

    def store_data_in_database(self, product_data):
        # store product details in database
        cursor = DB_CONN.cursor()
        for item in product_data:
            try:
                cursor.execute(
                    "INSERT INTO product_details (title, price, rating, url) VALUES (%s, %s, %s, %s)",
                    (
                        item["product_title"],
                        item["product_price"],
                        item["product_rating"],
                        item["product_url"],
                    ),
                )
            except Exception as e:
                logging.error(e)
        cursor.close()
