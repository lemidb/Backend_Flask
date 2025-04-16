from flask import Blueprint, jsonify, request
from app.models import User, db
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    
    new_user = User(username=data['username'], password=data['password'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token."""
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400    

    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.username)
    user_id = user.id
    user_name = user.username
    user_email = user.email
    return jsonify(user_id=user_id, user_name=user_name, user_email=user_email, access_token=access_token), 200
