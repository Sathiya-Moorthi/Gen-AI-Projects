# backend.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import os

app = Flask(__name__)

# --- NEW CONFIGURATION ---
# Get the absolute path of the directory where this script is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gym_log.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Data Model ---
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "exercise_name": self.exercise_name,
            "sets": self.sets,
            "reps": self.reps,
            "weight_kg": self.weight_kg,
            "volume": self.sets * self.reps * self.weight_kg
        }

with app.app_context():
    db.create_all()

# --- Endpoints ---

@app.route('/log', methods=['POST'])
def log_workout():
    data = request.get_json()
    if not data or not all(k in data for k in ('exercise_name', 'sets', 'reps', 'weight_kg')):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        sets = int(data['sets'])
        reps = int(data['reps'])
        weight = float(data['weight_kg'])

        if sets <= 0 or reps <= 0 or weight < 0:
            return jsonify({"error": "Positive numbers required."}), 400

        new_entry = WorkoutLog(
            date=datetime.now().strftime("%Y-%m-%d"),
            exercise_name=str(data['exercise_name']).strip(),
            sets=sets,
            reps=reps,
            weight_kg=weight
        )
        
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Logged!", "entry": new_entry.to_dict()}), 201

    except ValueError:
        return jsonify({"error": "Invalid data types."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    logs = WorkoutLog.query.order_by(WorkoutLog.id.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

@app.route('/progress', methods=['GET'])
def get_progress():
    """
    Aggregate volume by date.
    Supports optional query param: ?exercise=Name
    """
    try:
        # Check for 'exercise' query parameter
        exercise_filter = request.args.get('exercise')
        
        query = WorkoutLog.query
        
        # Apply filter if a specific exercise is requested
        if exercise_filter and exercise_filter != "All Exercises":
            # Case-insensitive comparison
            query = query.filter(func.lower(WorkoutLog.exercise_name) == exercise_filter.lower())
            
        logs = query.all()
        
        # Aggregate Data
        volume_map = {}
        for log in logs:
            vol = log.sets * log.reps * log.weight_kg
            if log.date in volume_map:
                volume_map[log.date] += vol
            else:
                volume_map[log.date] = vol
        
        progress_data = [{"date": k, "total_volume": v} for k, v in volume_map.items()]
        progress_data.sort(key=lambda x: x['date'])
        
        return jsonify(progress_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/log/<int:id>', methods=['DELETE'])
def delete_workout(id):
    """
    Delete a workout log by its ID.
    """
    try:
        log = WorkoutLog.query.get(id)
        if log:
            db.session.delete(log)
            db.session.commit()
            return jsonify({"message": "Deleted successfully"}), 200
        else:
            return jsonify({"error": "Log not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)