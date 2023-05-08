def init_urls_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scraped_urls (
            id SERIAL PRIMARY KEY,
            query VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            CONSTRAINT unique_query_url UNIQUE (query, url)
        )
    """
    )

    conn.commit()
    cursor.close()
