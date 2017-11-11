#!/usr/bin/env python3
import sqlite3
from config import db_file
conn = sqlite3.connect(db_file)
c = conn.cursor()

c.execute('''CREATE TABLE query (
            id INTEGER PRIMARY KEY ASC,
            name varchar(2048) NOT NULL,
            looked_up_at INTEGER NOT NULL,
            ip varchar(15) NOT NULL,
            type varchar(4) NOT NULL,
            method varchar(16),
            secure INTEGER
            )''')
conn.commit()
conn.close()
