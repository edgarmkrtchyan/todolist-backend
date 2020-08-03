from flask import Flask, jsonify, request, json
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)
from utils import utils

application = Flask(__name__)

appConfig = utils.getAppConfig()

application.config['MYSQL_USER'] = appConfig['user']
application.config['MYSQL_PASSWORD'] = appConfig['pwd']
application.config['MYSQL_DB'] = appConfig['db']
application.config['MYSQL_PORT'] = appConfig['port']
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# If using MAMP
application.config['MYSQL_UNIX_SOCKET'] = '/Applications/MAMP/tmp/mysql/mysql.sock'
application.config['JWT_SECRET_KEY'] = appConfig['jwt_key']

mysql = MySQL(application)
bcrypt = Bcrypt(application)
jwt = JWTManager(application)

CORS(application)

@application.route('/api/register', methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    payload = request.get_json()
    name = payload['name']
    surname = payload['surname']
    email = payload['email']
    password = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
    created_dt = datetime.utcnow()

    # TODO - handle the e-mail check to not exist
    cur.execute("INSERT INTO users (name, surname, email, password, created_dt) VALUES (%s,%s,%s,%s,%s)", (name, surname, email, password, created_dt))
    mysql.connection.commit()

    return jsonify({'status' : 'ok'})
	

@application.route('/api/login', methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    payload = request.get_json()
    email = payload['email']
    password = payload['password']
    result = ""
	
    cur.execute("SELECT * FROM users where email = '" + str(email) + "'")
    rv = cur.fetchone()
	
    if bcrypt.check_password_hash(rv['password'], password):
        expires = timedelta(minutes=30)
        access_token = create_access_token(expires_delta=expires, identity = {'name': rv['name'],'surname': rv['surname'],'email': rv['email']})
        result = jsonify({'status': 'ok', 'access_token': access_token})
    else:
        result = jsonify({'status': 'error', 'message': 'Invalid username or password'})
    
    return result

# CREATE A NEW TASK
@application.route('/api/task', methods=['POST'])
def create_task():
    cur = mysql.connection.cursor()
    payload = request.get_json()
    text = payload['text']
    priority = payload['priority']
    due_date = payload['due_date']
	
    cur.execute("INSERT INTO tasks (text, priority, due_date) VALUES (%s,%s,%s)", (text, priority, due_date))
    mysql.connection.commit()
    return jsonify({'status' : 'ok'})

# GET ALL TASKS
@application.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    cur = mysql.connection.cursor()
	
    cur.execute("SELECT * FROM tasks")
    rv = cur.fetchall()

    return jsonify({ 'status': 'ok', 'data': rv })

# UPDATE TASK BY ID
@application.route('/api/task/<int:id>', methods=['PUT'])
def update_task_by_id(id):
    cur = mysql.connection.cursor()
    payload = request.get_json()
    inputData = payload['input']
    queryParameters = ''

    # Forming the SQL query updates from the input object
    for param in inputData:
        queryParameters += param + '=' +  '"' + str(inputData[param]) + '",'
	
    queryParameters = queryParameters[:-1]

    cur.execute("UPDATE tasks SET " + queryParameters + " WHERE id = " + str(id))
    mysql.connection.commit()

    return jsonify({ 'status': 'ok' })
	
 # DELETE TASK BY ID
@application.route('/api/task/<int:id>', methods=['DELETE'])
def delete_task_by_id(id):
    cur = mysql.connection.cursor()
    response = cur.execute("DELETE FROM tasks where id=" + str(id))
    mysql.connection.commit()

    if response > 0:
        return jsonify({ 'status': 'ok' })
    else:
        return jsonify({ 'status': 'error', 'message': 'Task not found' })
	
# MARK TASK AS COMPLETED
@application.route('/api/task/complete/<int:id>', methods=['PUT'])
def complete_task(id):
    cur = mysql.connection.cursor()
	
    cur.execute("UPDATE tasks SET completed = 1 WHERE id = " + str(id))
    mysql.connection.commit()

    return jsonify({ 'status': 'ok' }) 

if __name__ == '__main__':
    application.run(debug=True)