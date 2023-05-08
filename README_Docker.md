Thank you for the additional information. Here's the updated `README.md` file:

# `README`

This repository contains a Python software for web scraping data from Amazon using two bots that communicate with each other through RabbitMQ. The software is packaged using Docker and managed using `docker-compose`.

## `Prerequisites`

To run this software, you will need to have Docker and `docker-compose` installed on your machine. You can download Docker [here](https://www.docker.com/products/docker-desktop) and `docker-compose` [here](https://docs.docker.com/compose/install/).

## `Installation`

To install and run the software, follow the steps below:

1. Clone this repository to your local machine using the command:

   ```bash
   $ git clone https://github.com/imzulkar/amazon-web-scrapping.git
   ```

2. Navigate to the project directory:

   ```bash
   $ cd amazon-web-scrapping
   ```

3. Create a `.env` file in the root directory and add the following environment variables:

- local .env configurations

  ```
  QUERY_PRODUCTS = iphone12, toys, shoes
  HOST = postgres
  PORT = 5432
  USER = postgres
  PASSWORD = postgres
  DATABASE = postgres
  ```

  **Note:** You can modify the values of these environment variables according to your requirements. The `QUERY_PRODUCTS` variable is used to set the product to be searched. Replace `QUERY_PRODUCTS` with the product you want to search for on Amazon.

4. Start the software using the following command:

   ```bash
   $ docker-compose up -d
   ```

5. Wait for the Docker containers to start. You can check the logs of each container using the following command:

   ```bash
   $ docker logs -f <container-name>
   ```

   **Note:** Replace `<container-name>` with the name of the container whose logs you want to check.

6. Once the containers are up and running, you can access the RabbitMQ management console by navigating to `http://localhost:15672` in your web browser. The default username and password are both `guest`.

## `Configuration`

This software uses the following Docker containers:

- `rabbitmq`: RabbitMQ message broker for communication between the bots.
- `postgres`: PostgreSQL database for storing the scraped data.
- `extractor`: Docker container for the bot that extracts data from Amazon.
- `scrapper`: Docker container for the bot that searches Amazon for product URLs.

You can configure these containers by modifying the `docker-compose.yml` file in the root directory of the project.

## `Usage`

Once the software is up and running, Bot will start scraping data from Amazon by sending a message to the `search_queue` in RabbitMQ. The `scrapper` bot will listen to this queue and start searching Amazon for the product specified in the `SEARCH_TERM` environment variable. Once a URL is found, the `scrapper` bot will send a message to the `extract_queue`, and the `extractor` bot will extract the required data from the product page and store it in the PostgreSQL database.

You can monitor the progress of the bots by checking the logs of the `extractor` and `scrapper` containers using the following command:

```bash
$ docker logs -f <container-name>
```

**`Note`:** Replace `<container-name>` with the name of the container whose logs you want to check.
