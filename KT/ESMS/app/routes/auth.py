from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.utils.security import generate_token, hash_password, check_password

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed = hash_password(data['password'])
    user = User(
        email=data['email'],
        password_hash=hashed,
        role=data['role'],
        department=data.get('department'),
        manager_id=data.get('manager_id')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password(data['password'], user.password_hash):
        token = generate_token(user.id, user.role)
        return jsonify({'token': token, 'role': user.role}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401
