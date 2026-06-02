from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'todo.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       description
                       TEXT,
                       status
                       TEXT
                       DEFAULT
                       'pending',
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       completed_at
                       TIMESTAMP
                   )
                   ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    conn.close()

    tasks_list = [dict(task) for task in tasks]
    return render_template('index.html', tasks=tasks_list)


@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if title:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (title, description) VALUES (?, ?)',
            (title, description)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
        ('completed', datetime.now(), task_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/pending/<int:task_id>')
def pending_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
        ('pending', None, task_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)