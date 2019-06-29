#!/usr/bin/env python

import os
import psycopg2
import urllib.parse as up


if __name__ == '__main__':
    up.uses_netloc.append("postgres")

    url = up.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port
                            )

    cur = conn.cursor()
    cur.execute("SELECT * FROM test_schema.test;")
    print(cur.fetchone())

    conn.close()