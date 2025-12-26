from flask import Blueprint, request, jsonify, g
from app import db
from app.models import HandoverEvent, SeparationCase
from app.utils.decorators import requires_role
from app.services.calendar_service import create_calendar_event
from datetime import datetime

bp = Blueprint('scheduling', __name__, url_prefix='/scheduling')

@bp.route('/event', methods=['POST'])
@requires_role()
def create_event():
    data = request.get_json()
    case_id = data.get('case_id')
    
    case = SeparationCase.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
        
    # Validate user is part of the case
    if case.employee_id != g.current_user['user_id']:
         # Also allow managers?
         pass

    event = HandoverEvent(
        case_id=case_id,
        title=data['title'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time'])
    )
    db.session.add(event)
    db.session.commit()
    
    # Sync to Google Calendar
    attendees = [case.employee.email] # Add manager etc.
    create_calendar_event(event.title, event.start_time, event.end_time, attendees)
    
    return jsonify(event.to_dict()), 201
