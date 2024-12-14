from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    connection = sqlite3.connect('blog.db')
    connection.row_factory = sqlite3.Row
    return connection

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        user = connection.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                                   (username, password)).fetchone()
        connection.close()
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
    return redirect(url_for('login'))

# Dashboard and Blog Routes
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts WHERE author_id = ? ORDER BY created_at DESC", 
                                (session['user_id'],)).fetchall()
    connection.close()
    return render_template('dashboard.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        connection = get_db_connection()
        try:
            connection.execute("INSERT INTO posts (title, content, author_id, created_at) VALUES (?, ?, ?, ?)", 
                               (title, content, session['user_id'], datetime.now()))
            connection.commit()
            flash('Post created successfully.')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Error creating post: {e}')
        finally:
            connection.close()
    return render_template('new_post.html')

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ? AND author_id = ?", 
                               (post_id, session['user_id'])).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        try:
            connection.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?", 
                               (title, content, post_id))
            connection.commit()
            flash('Post updated successfully.')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Error updating post: {e}')
        finally:
            connection.close()
    connection.close()
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete')
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    connection = get_db_connection()
    try:
        connection.execute("DELETE FROM posts WHERE id = ? AND author_id = ?", 
                           (post_id, session['user_id']))
        connection.commit()
        flash('Post deleted successfully.')
    except sqlite3.Error as e:
        flash(f'Error deleting post: {e}')
    finally:
        connection.close()
    return redirect(url_for('dashboard'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT posts.*, users.username AS author FROM posts JOIN users ON posts.author_id = users.id WHERE posts.id = ?", 
                               (post_id,)).fetchone()
    connection.close()
    return render_template('view_post.html', post=post)

# User Registration (Optional for Admin Only)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        try:
            connection.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                               (username, password))
            connection.commit()
            flash('User registered successfully.')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Error registering user: {e}')
        finally:
            connection.close()
    return render_template('register.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
