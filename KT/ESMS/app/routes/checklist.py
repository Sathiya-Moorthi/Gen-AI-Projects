from flask import Blueprint, request, jsonify, g
from app import db
from app.models import ChecklistItem, SeparationCase
from app.utils.decorators import requires_role
from app.services.email_service import send_email

bp = Blueprint('checklist', __name__, url_prefix='/checklist')

@bp.route('/<int:case_id>', methods=['GET'])
@requires_role() # Any authenticated user involved can view? Let's restrict to owner and relevant depts
def get_checklist(case_id):
    # TODO: Add finer grained permission check
    items = ChecklistItem.query.filter_by(case_id=case_id).all()
    return jsonify([item.to_dict() for item in items]), 200

@bp.route('/<int:item_id>', methods=['PUT'])
@requires_role() # Needs to be the department owner or admin
def update_checklist_item(item_id):
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
        
    # Check permissions: User role must match item department
    user_role = g.current_user['role']
    # Mapping roles to departments (simplified)
    # IT -> IT, Finance -> Finance, Direct_Manager -> Manager
    
    allowed = False
    if user_role == item.department:
        allowed = True
    elif user_role == 'Direct_Manager' and item.department == 'Manager':
        allowed = True
    elif user_role == 'Separation_Manager': # Admin can override
        allowed = True
        
    if not allowed:
        return jsonify({'error': 'Unauthorized to update this item'}), 403
        
    data = request.get_json()
    item.completed = data.get('completed', item.completed)
    db.session.commit()
    
    # Check if all items are complete
    case = SeparationCase.query.get(item.case_id)
    all_complete = all(i.completed for i in case.checklists)
    
    if all_complete:
        send_email(case.employee.email, "Checklist Completed", "All checklist items have been completed.")
        
    return jsonify(item.to_dict()), 200
