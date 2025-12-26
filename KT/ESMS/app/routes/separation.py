from flask import Blueprint, request, jsonify, g
from app import db
from app.models import SeparationCase, User, ChecklistItem, SignoffLog
from app.utils.decorators import requires_role
from app.services.email_service import send_email

bp = Blueprint('separation', __name__, url_prefix='/separation')

@bp.route('/initiate', methods=['POST'])
@requires_role('Employee')
def initiate_separation():
    user_id = g.current_user['user_id']
    
    # Check if already initiated
    existing_case = SeparationCase.query.filter_by(employee_id=user_id, status='Initiated').first()
    if existing_case:
        return jsonify({'error': 'Separation already initiated'}), 400
    
    case = SeparationCase(employee_id=user_id)
    db.session.add(case)
    db.session.commit()
    
    # Create default checklist items
    items = [
        ChecklistItem(case_id=case.id, description='Return Laptop', department='IT'),
        ChecklistItem(case_id=case.id, description='Clear Dues', department='Finance'),
        ChecklistItem(case_id=case.id, description='Handover Knowledge', department='Manager')
    ]
    db.session.add_all(items)
    db.session.commit()
    
    # Notify Manager
    user = User.query.get(user_id)
    if user.manager:
        send_email(user.manager.email, "Separation Initiated", f"Employee {user.email} has initiated separation.")
    
    return jsonify({'message': 'Separation initiated', 'case_id': case.id}), 201

@bp.route('/my-status', methods=['GET'])
@requires_role('Employee')
def my_status():
    user_id = g.current_user['user_id']
    case = SeparationCase.query.filter_by(employee_id=user_id).order_by(SeparationCase.created_at.desc()).first()
    
    if not case:
        return jsonify({'message': 'No active separation case'}), 404
        
    return jsonify(case.to_dict()), 200

@bp.route('/approve', methods=['POST'])
@requires_role(['Direct_Manager', 'Separation_Manager']) # Allow both for now, logic can be refined
def approve_separation():
    data = request.get_json()
    case_id = data.get('case_id')
    action = data.get('action') # Approved, Rejected
    
    case = SeparationCase.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
        
    signer_id = g.current_user['user_id']
    signer = User.query.get(signer_id)
    
    # Log signoff
    log = SignoffLog(
        case_id=case.id,
        signer_id=signer_id,
        department=signer.department or 'Management',
        action=action
    )
    db.session.add(log)
    
    if action == 'Approved':
        case.status = 'ManagerApproved'
        # Logic to move to next stage or notify departments
    elif action == 'Rejected':
        case.status = 'Rejected'
        
    db.session.commit()
    
    return jsonify({'message': f'Separation {action}'}), 200
