import sqlite3

connection = sqlite3.connect('blog.db')
cursor = connection.cursor()

with open('Schema.sql') as f:
    cursor.executescript(f.read())

cursor.execute("""
    INSERT INTO users (username, password) VALUES (?, ?)
""", ("admin", "admin123"))  

cursor.execute("""
    INSERT INTO posts (title, content, author_id, created_at)
    VALUES (?, ?, ?, ?)
""", ("Welcome to My Blog", "This is the first post on my blog!", 1, "2024-12-14 10:00:00"))

connection.commit()
connection.close()
