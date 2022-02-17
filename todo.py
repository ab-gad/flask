from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# username and password for testing 
USERNAME = "admin"
PASSWORD = "0000"

app = Flask(__name__)

# jwt configuration
app.config['JWT_SECRET_KEY'] = "secrt1246"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# in case you wanna change ur token location
# app.config['JWT_token_LOCATION'] = ['cookies']
# it will be send in the request header by default

jwt = JWTManager(app)

# setting our DB settiongs
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://team4:0000@localhost:5432/flask'
db = SQLAlchemy(app)

#########
# MODLES
#########

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True ,autoincrement = True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"Category ('{self.name}')"


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id  = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship("Category", foreign_keys = [category_id])

    def __repr__(self):
        return f'Task("{self.title}", "{self.created_at}")'

db.create_all() # migration

# defining our api endpoints

@app.route('/category', methods=['GET', 'POST'])
def category():
    if request.method == 'GET':
        all_categories = Category.query.all() #>> Quryset
        result = []
        for c in all_categories:
            dict = {}
            dict['id'] = c.id
            dict['name'] = c.name
            result.append(dict)

        return jsonify({
            "categories":result
        })

    elif request.method == 'POST':

        id = request.json.get('id')
        name = request.json.get('name')
        
        # data = json.loads(request.data)
        
        category = Category(id=id, name=name)
        db.session.add(category)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"{name} catigory added successfully"
        })

@app.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        all_tasks = Task.query.all() 
        result = []
        for t in all_tasks:
            dict = {}
            cat = Category.query.filter_by(id=t.category_id).first()

            dict['id'] = t.id
            dict['title'] = t.title
            dict['details'] = t.details
            dict['created_at'] = t.created_at
            dict['catigory'] = cat.name

            result.append(dict)

        return jsonify({
            "status":"success",
            "data": result
        })

    if request.method == 'POST':

        # data = json.loads(request.data)
        # title = data["title"]

        title = request.json.get('title')
        details = request.json.get('details')
        created_at = request.json.get('created_at')
        category_id = request.json.get('category_id')

        newTask = Task(title=title, details=details, created_at=created_at, category_id=category_id)
        db.session.add(newTask)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": f"task {title} added successfully"
        })

@app.route('/task/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def edit_task(id):
    username = get_jwt_identity()
    print(username)
    t= Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        cat = Category.query.filter_by(id=t.category_id).first()

        dict['id'] = t.id
        dict['title'] = t.title
        dict['details'] = t.details
        dict['created_at'] = t.created_at
        dict['catigory'] = cat.name

        return jsonify({
            "data":dict
        })

    if request.method == 'PUT':
        if request.json.get('title'):
            t.title = request.json.get('title')
        if request.json.get('details'):
            t.details = request.json.get('details')
        if request.json.get('category_id'):
            t.category_id = request.json.get('category_id')

        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user upadted successfully"
        })
    
    if request.method == 'DELETE':
        db.session.delete(t)
        db.session.commit()

        return jsonify({
            "status":"success",
            "data": "user deleted successfully"
        })

# authentication end points
@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    if data['username'] == USERNAME and data['password'] == PASSWORD:
        access_token = create_access_token(identity=data["username"]) 

        return jsonify({
            "status" : "success",
            "data" : {'access_token': access_token}
        })

    else:
        return jsonify({
            "status" : "failure auth",
            'msg': 'wrong username or password' 
        })
    

@app.route('/')
def home():
    return "<h1> HELLO WORLD </h1>"

app.run(host='127.0.0.1', port=5000, debug=True)