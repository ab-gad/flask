from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


# DATABASE_URI='sqlite://users.db'
DATABASE_URI='postgres://team4:0000@localhost:5432/flask'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

db = SQLAlchemy(app)

class Department(db.Model):
    __tablename__ = 'department' 
    id = db.Column(db.Integer, primary_key=True ,autoincrement = True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"Deaprtment ('{self.name}')"


class User(db.Model):
    #table name is class name in lowercase by default
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    ceated_at = db.Column(db.DateTime, default=datetime.utcnow)
    department_id  = db.Column(db.Integer, db.ForeignKey('department.id'))

    department = db.relationship("Deapartment", foreign_keys = [department_id])

    def __repr__(self):
        return f'User("{self.username}", "{self.email}")'


db.create_all() # migration

@app.route('/department', mehthods=['GET', 'POST'])
def department():
    if request.method == 'GET':
        all_departments = Department.query.all() #>> Quryset
        # department = Department.query.get(id) #>> a deaprtment
        # filter_department = Department.query.filter_by(name = "HR")
        # filter_department_1st = Department.query.filter_by(name = "HR").first()
        result = []
        for d in all_departments:
            dict = {}
            dict['id'] = d.id
            dict['name'] = d.name
            result.append(dict)

        return jsonify({
            "depatments":result
        })
    elif request.method == 'POST':
        id = request.json.get('id') 
        name = request.json.get('name')

        #another method to reteive data
        data = json.loads(request.data)
        # id = data['id']
        # name = data['name']

        department = Department(id=id, name=name)
        db.session.add(department)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"{name} department added successfully"
        })

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'GET':
        users = User.query.all()
        result = []
        for u in users:
            dict = {}
            dept = Department.query.filter_by(id=u.department_id).first()

            dict['id'] = u.id
            dict['username'] = u.username
            dict['email'] = u.email
            dict['ceated_at'] = u.ceated_at
            dict['dept Name'] = dept.name

            result.append(dict)
        
        return jsonify({
            "status":"success",
            "data": result
        })

    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        department_id = request.json.get('department_id')

        newUser = User(username=username, password=password, email=email, department_id=department_id)
        db.session.add(newUser)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"{username} added successfully"
        })

@app.route('/user/<int:id>', methods=['GET', 'DELETE', 'PUT'])
def edit_user(id):
    u= User.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        dict['id'] = u.id
        dict['username'] = u.username
        dict['email'] = u.email
        dict['ceated_at'] = u.ceated_at
        dict['dept Name'] = Department.query.filter_by(id=u.department_id).first().name

        return jsonify({
            "data":dict
        })

    if request.method == 'PUT':
        u.email = request.json.get('email')
        u.password = request.json.get('password')

        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user upadted successfully"
        })
    
    if request.method == 'DELETE':
        db.session.delete(u)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user deleted successfully"
        })

@app.route('/')
def home():
    return "<h1> HELLO WORLD </h1>"

app.run(host='127.0.0.1', port=5000, debug=True)

# from flask import Flask, render_template, jsonify, request

# app = Flask(__name__)

# users = [
#     {"id": 1, "username": "Ahmed", "age": 50},
#     {"id": 2, "username": "test", "age": 40},
#     {"id": 3, "username": "mohamed", "age": 30},
# ]


# @app.route('/', methods=['Get'])
# def home():
#     return jsonify({
#         "users": users
#     })


# @app.route('/create', methods=['POST'])
# def create():
#     id = request.json.get('id')
#     username = request.json.get('username')
#     age = request.json.get('age')
#     users.append({
#         'id': id,
#         'username': username,
#         'age': age
#     })
#     return jsonify({'users': users})


# @app.route('/DELETE/<int:id>', methods=['POST'])
# def Delete(id):
#     for user in users:
#         print(user['id'])
#         if user['id'] == id:
#             users.remove(user)
#             return jsonify({
#                 "msg": "deleted"
#             })
#         else:
#             return jsonify({
#                 "msg": "notfound"
#             })


# @app.route('/UPDATE/<int:id>', methods=['POST'])
# def UPDATE(id):
#     for user in users:
#         if user['id'] == id:
#             user['id'] = request.json.get('id')
#             user['username'] = request.json.get('username')
#             user['age']= request.json.get('age')

#             return jsonify({'users': users})
#         else:
#             return jsonify({"msg": "notfound"})


# app.run(host='127.0.0.1', port=5000, debug=True)
