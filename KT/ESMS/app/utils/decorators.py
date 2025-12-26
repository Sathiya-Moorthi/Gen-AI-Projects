from functools import wraps
from flask import request, jsonify, g
from app.utils.security import verify_token

def requires_role(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid token'}), 401
            
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check role hierarchy or exact match
            # For simplicity, we'll do exact match or list of allowed roles
            # If required_role is a list, check if user role is in it
            # If required_role is a string, check exact match
            
            user_role = payload['role']
            
            if required_role:
                if isinstance(required_role, list):
                    if user_role not in required_role:
                         return jsonify({'error': 'Insufficient permissions'}), 403
                elif user_role != required_role:
                    # Allow Admin/Separation_Manager to access everything? Maybe not.
                    # Let's stick to explicit checks for now.
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            g.current_user = payload # Store user info in g
            return f(*args, **kwargs)
        return decorated_function
    return decorator
