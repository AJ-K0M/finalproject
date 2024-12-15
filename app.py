from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute("""
        SELECT posts.*, users.username AS author 
        FROM posts JOIN users ON posts.author_id = users.id
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Try a different one.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    posts = conn.execute("""
        SELECT * FROM posts WHERE author_id = ? ORDER BY created_at DESC
    """, (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO posts (title, content, author_id, created_at)
            VALUES (?, ?, ?, ?)
        """, (title, content, session['user_id'], datetime.now()))
        conn.commit()
        conn.close()
        flash('Post created successfully.')
        return redirect(url_for('dashboard'))
    return render_template('new_post.html')

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ? AND author_id = ?", 
                        (post_id, session['user_id'])).fetchone()
    if not post:
        flash('Post not found or permission denied.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?", 
                     (title, content, post_id))
        conn.commit()
        conn.close()
        flash('Post updated successfully.')
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ? AND author_id = ?", 
                 (post_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Post deleted successfully.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
