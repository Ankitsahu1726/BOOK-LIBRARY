from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'library.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT,
            action TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/')
def home():
    search = request.args.get('search', '')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search:
        cursor.execute('''
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ?
        ''', (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute('SELECT * FROM books')

    books = cursor.fetchall()

    cursor.execute('SELECT * FROM history ORDER BY id DESC')
    history = cursor.fetchall()

    conn.close()

    return render_template('index.html', books=books, history=history)


@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    category = request.form['category']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO books (title, author, category)
        VALUES (?, ?, ?)
    ''', (title, author, category))

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/borrow/<int:book_id>')
def borrow_book(book_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT title FROM books WHERE id=?', (book_id,))
    book = cursor.fetchone()

    cursor.execute('''
        UPDATE books
        SET status='Borrowed'
        WHERE id=?
    ''', (book_id,))

    cursor.execute('''
        INSERT INTO history (book_title, action, date)
        VALUES (?, ?, ?)
    ''', (
        book[0],
        'Borrowed',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/return/<int:book_id>')
def return_book(book_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT title FROM books WHERE id=?', (book_id,))
    book = cursor.fetchone()

    cursor.execute('''
        UPDATE books
        SET status='Available'
        WHERE id=?
    ''', (book_id,))

    cursor.execute('''
        INSERT INTO history (book_title, action, date)
        VALUES (?, ?, ?)
    ''', (
        book[0],
        'Returned',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)