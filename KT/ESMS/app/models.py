from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # Employee, Direct_Manager, Separation_Manager, IT, Finance
    department = db.Column(db.String(50))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    manager = db.relationship('User', remote_side=[id], backref='subordinates')
    separation_cases = db.relationship('SeparationCase', backref='employee', foreign_keys='SeparationCase.employee_id')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'manager_id': self.manager_id
        }

class SeparationCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Initiated')  # Initiated, ManagerApproved, DeptProcessing, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checklists = db.relationship('ChecklistItem', backref='case', lazy=True)
    signoffs = db.relationship('SignoffLog', backref='case', lazy=True)
    handover_events = db.relationship('HandoverEvent', backref='case', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('separation_case.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(50), nullable=False) # IT, Finance, Manager
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'description': self.description,
            'department': self.department,
            'completed': self.completed
        }

class SignoffLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('separation_case.id'), nullable=False)
    signer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False) # Approved, Rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'signer_id': self.signer_id,
            'department': self.department,
            'action': self.action,
            'timestamp': self.timestamp.isoformat()
        }

class HandoverEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('separation_case.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
