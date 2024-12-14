import sqlite3

# Connect to SQLite database
connection = sqlite3.connect('blog.db')
cursor = connection.cursor()

# Read schema file and execute it
with open('Schema.sql') as f:
    cursor.executescript(f.read())

# Insert a sample user (username: admin, password: admin123)
cursor.execute("""
    INSERT INTO users (username, password) VALUES (?, ?)
""", ("admin", "admin123"))  # Password should be hashed in production

# Insert a sample post by the admin user
cursor.execute("""
    INSERT INTO posts (title, content, author_id, created_at)
    VALUES (?, ?, ?, ?)
""", ("Welcome to My Blog", "This is the first post on my blog!", 1, "2024-12-14 10:00:00"))

# Commit and close the connection
connection.commit()
connection.close()
