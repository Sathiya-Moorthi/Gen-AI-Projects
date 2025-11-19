import datetime
import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Configuration
app = Flask(__name__)
# Using SQLite for persistence. 
# SQLAlchemy handles SQL injection protection automatically.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hydration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_ml = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'amount_ml': self.amount_ml,
            'timestamp': self.timestamp.isoformat()
        }

# --- Helper: Data Seeder ---
def seed_data():
    """Populates the DB with 1 week of sample data if empty."""
    if WaterLog.query.first() is None:
        print("Seeding database with sample data...")
        today = datetime.datetime.now()
        for i in range(7, 0, -1):
            day_date = today - datetime.timedelta(days=i)
            # Add 3 random drinks per day
            for _ in range(3):
                vol = random.choice([250, 500, 330])
                log = WaterLog(amount_ml=vol, timestamp=day_date)
                db.session.add(log)
        db.session.commit()
        print("Database seeded.")

# --- API Endpoints ---

@app.route('/log', methods=['POST'])
def log_water():
    """
    Receives JSON: {"amount": int}
    Validates input and saves to DB.
    """
    data = request.get_json()
    
    if not data or 'amount' not in data:
        return jsonify({'error': 'Missing amount parameter'}), 400
    
    amount = data['amount']

    # Input Validation: strictly positive integers
    if not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Amount must be a positive integer'}), 400

    new_log = WaterLog(amount_ml=amount)
    db.session.add(new_log)
    db.session.commit()

    return jsonify({'message': 'Logged successfully', 'entry': new_log.to_dict()}), 201

@app.route('/summary', methods=['GET'])
def get_summary():
    """Calculates today's total vs Goal."""
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # SQL Logic: Sum amount_ml where timestamp >= today
    total_today = db.session.query(func.sum(WaterLog.amount_ml))\
        .filter(WaterLog.timestamp >= today_start).scalar() or 0

    return jsonify({
        'date': today_start.isoformat(),
        'total_ml': total_today,
        'goal_ml': 3000,
        'percentage': min((total_today / 3000) * 100, 100) # Cap at 100 for logic
    })

@app.route('/history', methods=['GET'])
def get_history():
    """Returns raw log data for the last 7 days for visualization."""
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    logs = WaterLog.query.filter(WaterLog.timestamp >= seven_days_ago).all()
    return jsonify([log.to_dict() for log in logs])

# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates hydration.db if not exists
        seed_data()     # Inject sample data
    
    # Run Flask on port 5000
    app.run(debug=True, port=5000)