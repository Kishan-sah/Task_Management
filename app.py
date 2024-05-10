#create flask app
import datetime
from os import path
from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)

# Initialize the database only if the database does not exist yet
if not path.exists('task.db'):
    with app.app_context():
        db.create_all()
    def __repr__(self):
        return f"Task('{self.id}', '{self.title}', '{self.description}', '{self.due_date}')"


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retrieves all tasks from the database and renders the 'task.html' template with the task data.

    Returns:
        A rendered template 'task.html' with the task data.
    """
    tasks = Task.query.all()
    return render_template('task.html', tasks=tasks)
   


@app.route('/create_task', methods=['GET','POST'])
def create_task():
    """
    Creates a new task.

    This function is a route handler for the '/create_task' endpoint. It handles both GET and POST requests.
    
    Parameters:
        None
    
    Returns:
        - If the request method is GET, it renders the 'create_task.html' template.
        - If the request method is POST, it creates a new task using the form data from the request. The task is then added to the database and the 'single-task.html' template is rendered with the created task data.
    """
    if request.method == 'GET':
        return render_template('create_task.html')
    else:
        title = request.form['title']
        description = request.form['description']
        due_date = datetime.datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        task = Task(title=title, description=description, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        return render_template('single-task.html', task=task)


@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    """
    Retrieves a task with the given ID from the database and renders the 'single-task.html' template with the task data.

    Parameters:
        id (int): The ID of the task to retrieve.

    Returns:
        If the task is found, renders the 'single-task.html' template with the task data.
        If the task is not found, returns a JSON response with an error message and a status code of 404.
    """
    task = Task.query.get(id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return render_template('single-task.html', task=task)


@app.route('/update_task/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    """
    Updates a task with the given ID.

    Args:
        id (int): The ID of the task to be updated.

    Returns:
        If the task is found and updated successfully, returns the rendered template 'single-task.html' with the updated task.
        If the task is not found, returns a JSON response with an error message and a status code of 404.
        If the request method is 'GET', returns the rendered template 'update_task.html' with the task to be updated.
    """
    task = Task.query.get(id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    if request.method == 'GET':
        return render_template('update_task.html', task=task)
    else:
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = datetime.datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        db.session.commit()
        return render_template('single-task.html', task=task)


@app.route('/delete_task/<int:id>')
def delete_task(id):
    """
    Deletes a task with the given ID.

    Args:
        id (int): The ID of the task to be deleted.

    Returns:
        If the task is found and deleted successfully, redirects to the 'get_tasks' route.
        If the task is not found, returns a JSON response with an error message and a status code of 404.
    """
    task = Task.query.get(id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('get_tasks'))


if __name__ == '__main__':
    app.run(debug=True)

