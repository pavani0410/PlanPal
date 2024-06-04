from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        activity = request.form['activity']
        date_finish_by = request.form['date_finish_by']
        progress = request.form['progress']
        task_id = request.form.get('task_id')

        conn = get_db_connection()
        
        if task_id:  
            conn.execute('UPDATE ToDoList SET Activity = ?, Date_FinishBy = ?, Progress = ? WHERE No = ?',
                         (activity, date_finish_by, progress, task_id))
            print(f"Updated ToDo item with ID {task_id} in the Database")
        else:  
            date_entered = date.today().strftime("%Y-%m-%d")
            conn.execute('INSERT INTO ToDoList (Activity, Date_Entered, Date_FinishBy, Progress) VALUES (?, ?, ?, ?)',
                         (activity, date_entered, date_finish_by, progress))
            print("Added to Database")
        
        conn.commit()
        conn.close()
        return redirect(url_for('view_todo'))
    
    todos = get_db_connection().execute('SELECT * FROM ToDoList').fetchall()
    return render_template('todo.html', todos=todos)

@app.route('/view_todo')
def view_todo():
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM ToDoList').fetchall()
    conn.close()
    return render_template('view_todo.html', todos=todos)

@app.route('/delete_todo/<int:id>', methods=['POST'])
def delete_todo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ToDoList WHERE No = ?', (id,))
    conn.commit()
    conn.close()
    print(f"Deleted ToDo item with ID {id} from Database")
    return redirect(url_for('view_todo'))


@app.route('/note', methods=['GET', 'POST'])
def note():
    if request.method == 'POST':
        title = request.form['title']
        date_entered = date.today().strftime("%Y-%m-%d")
        subnote = request.form.get('subnote', '')  
        conn = get_db_connection()
        conn.execute('INSERT INTO Notes (Title, Date_Entered) VALUES (?, ?)', 
                     (title, date_entered))
        conn.commit()
        conn.close()
        print("Added Note to Database")
        return redirect(url_for('view_notes'))
    return render_template('note.html')

@app.route('/view_notes')
def view_notes():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM Notes').fetchall()
    conn.close()
    return render_template('view_notes.html', notes=notes)

@app.route('/delete_note/<string:title>', methods=['POST'])
def delete_note(title):
    conn = get_db_connection()
    conn.execute('DELETE FROM Notes WHERE Title = ?', (title,))
    conn.commit()
    conn.close()
    print(f"Deleted Note with Title '{title}' from Database")
    return redirect(url_for('view_notes'))


if __name__ == '__main__':
    with app.app_context():
        conn = get_db_connection()
        conn.execute('CREATE TABLE IF NOT EXISTS ToDoList (No INTEGER PRIMARY KEY AUTOINCREMENT, Activity TEXT, Date_Entered DATE, Date_FinishBy DATE, Progress TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS Notes (Title TEXT, Date_Entered DATE)')
        conn.close()
    app.run(debug=True)