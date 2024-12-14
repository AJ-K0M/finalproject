import sqlite3

# Connect to the database or create it if it doesn't exist
connection = sqlite3.connect('blog.db')
cursor = connection.cursor()

# Execute schema script to create tables
with open('schema.sql') as f:
    cursor.executescript(f.read())

# Insert sample user
cursor.execute("""
    INSERT INTO users (username, password, email)
    VALUES (?, ?, ?, ?, ?)
""", ("John1234", "admin123") "john@example.com"))  # Password should be hashed in production

# Insert sample posts
cursor.execute("""
    INSERT INTO posts (title, content, author_id, created_at)
    VALUES (?, ?, ?, ?)
""", ("Welcome to My Blog", "This is the first blog post.", 1, "2024-12-14 10:00:00"))

cursor.execute("""
    INSERT INTO posts (title, content, author_id, created_at)
    VALUES (?, ?, ?, ?)
""", ("Another Post", "This is another blog post content.", 1, "2024-12-14 11:00:00"))

# Commit changes and close the connection
connection.commit()
connection.close()
