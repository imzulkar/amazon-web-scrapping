# `README`

This repository contains a Python software for web scraping data from Amazon using two bots that communicate with each other through RabbitMQ. The software is packaged using selenium.

## `Installation`

To install this software, follow the steps below:

1. Clone the repository to your local machine.

   ```bash
   $ git clone https://github.com/imzulkar/amazon-web-scrapping.git
   ```

2. Install Pipenv by running the following command in your terminal:

   ```bash
   $ pip install pipenv
   ```

3. Navigate to the project directory in your terminal and run the following command to install the required dependencies:

   ```bash
   $ pipenv install
   ```

4. Running the Application with Docker Compose for rabbitmq & postgres:

   ```bash
   $ docker-compose up -d
   ```

- `NOTE`: Before run previous line please comment below section from `docker-compose.yml`

  ```
  extractor:
     image: extractor
     container_name: 'extractor'
     build:
     context: .
     dockerfile: extractor/Dockerfile
     #when building
     shm_size: 1gb
     #when running
     shm_size: 1gb
     volumes:
     - ./logs:/code/logs:rw
     depends_on:
     - postgres

  scrapper:
     image: scrapper
     container_name: 'scrapper'
     build:
     context: .
     dockerfile: scrapper/Dockerfile
     #when building
     shm_size: 1gb
     #when running
     shm_size: 1gb
     volumes:
     - ./logs:/code/logs:rw
     depends_on:
     - extractor
     env_file:
     - .env

  ```

## `.ENV Configurations`

### Create a .env file in the root directory and add the following environment variables:

- local .env configurations

  ```bash
  QUERY_PRODUCTS = iphone12, toys, shoes

  HOST = hostName
  PORT = 5432
  USER = userName
  PASSWORD = Password
  DATABASE = databaseName
  ```

  **Note:** You can modify the values of these environment variables according to your requirements. The `QUERY_PRODUCTS` variable is used to set the product to be searched. Replace `QUERY_PRODUCTS` with the product you want to search for on Amazon.

## `Usage`

To use this software, follow the steps below:

1. Run the following command in your terminal to activate the Pipenv shell:

   ```bash
   $ pipenv shell
   ```

2. Run the following command in your terminal to run the script:

   ```bash
   $ pipenv run <script_name>
   ```

   Replace `<script_name>` with the name of your custom script name

   - First run extractor then run scrapper in diffrent terminal for local use

## `Outputs`

The output response will saved in logs directory,

1. logs/products_url for
2. Also data stored in PostgresSQL.

## `Docker configurations`

For Docker configurations, please see the [Docker.md](README_Docker.md) file.
