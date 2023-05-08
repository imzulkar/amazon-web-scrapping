from selenium import webdriver
from selenium.webdriver.common.by import By
from extractor.__init__ import RMQ_CONN, DB_CONN
import json


class Product:
    def __init__(self):
        self.channel = self.setup_rabbitmq()
        # self.consume_product_urls()
        print("Product initialized")
        self.consume_status()

    def scrapper_comm(self, data):
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
        message_body = json.loads(body.decode())
        print(message_body)
        if message_body["message"] == "ping":
            self.scrapper_comm({"message": "pong"})
        elif message_body["message"] == "start":
            self.process_product_scrapping_op(message_body["query"])
        else :
            pass

    def process_product_scrapping_op(self, search_query):
        product_urls = self.get_urls_from_db(search_query)
        product_data = self.scrape_product(product_urls)
        self.store_data_in_database(product_data)
        self.log_data(search_query, product_data)
        self.scrapper_comm({"message": "reset"})

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

    def get_urls_from_db(self, query):
        cursor = DB_CONN.cursor()
        cursor.execute("SELECT url FROM scraped_urls WHERE query=%s", (query,))
        results = cursor.fetchall()
        urls = [row[0] for row in results]
        cursor.close()
        return urls

    def scrape_product(self, product_urls):
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

            product = {
                "product_title": product_title,
                "product_price": product_price,
                "product_rating": product_rating,
                "product_url": item,
            }
            print(product)
            products.append(product)

        driver.quit()

        return products

    def log_data(self, search_query, data):
        with open(f"scraped_products_for_{search_query}.json", "w") as f:
            json.dump(data, f)

    def store_data_in_database(self, product_data):
        for item in product_data:
            print(
                (
                    item["product_title"],
                    item["product_price"],
                    item["product_rating"],
                    item["product_url"],
                )
            )
            try:
                cursor = DB_CONN.cursor()
                cursor.execute(
                    "INSERT INTO product_details (title, price, rating, url) VALUES (%s, %s, %s, %s)",
                    (
                        item["product_title"],
                        item["product_price"],
                        item["product_rating"],
                        item["product_url"],
                    ),
                )
                DB_CONN.commit()
                cursor.close()
            except Exception as e:
                print(e)
