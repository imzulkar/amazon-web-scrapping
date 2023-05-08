def product_details(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_details (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price VARCHAR(10) NOT NULL,
            rating VARCHAR(5) NOT NULL,
            url TEXT NOT NULL
        )
        """
    )

    conn.commit()
    cursor.close()
