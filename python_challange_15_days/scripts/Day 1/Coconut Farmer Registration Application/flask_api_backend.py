from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class FarmerDatabase:
    """Simple file-based database for farmer data"""
    
    def __init__(self, filename: str = "farmers_data.json"):
        self.filename = filename
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
            else:
                # Initialize with empty structure
                return {
                    "farmers": {},
                    "next_id": 1,
                    "total_registrations": 0,
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {"farmers": {}, "next_id": 1, "total_registrations": 0}
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def get_next_id(self) -> int:
        """Get next available farmer ID"""
        next_id = self.data["next_id"]
        self.data["next_id"] += 1
        return next_id
    
    def add_farmer(self, farmer_data: Dict) -> int:
        """Add new farmer to database"""
        farmer_id = self.get_next_id()
        farmer_data["id"] = farmer_id
        farmer_data["registration_date"] = datetime.now().isoformat()
        farmer_data["last_updated"] = datetime.now().isoformat()
        
        self.data["farmers"][str(farmer_id)] = farmer_data
        self.data["total_registrations"] += 1
        self._save_data()
        
        logger.info(f"Added new farmer: {farmer_data['name']} (ID: {farmer_id})")
        return farmer_id
    
    def update_farmer(self, farmer_id: int, updated_data: Dict) -> bool:
        """Update existing farmer data"""
        farmer_key = str(farmer_id)
        if farmer_key not in self.data["farmers"]:
            return False
        
        # Update only provided fields
        for key, value in updated_data.items():
            if key in self.data["farmers"][farmer_key]:
                self.data["farmers"][farmer_key][key] = value
        
        self.data["farmers"][farmer_key]["last_updated"] = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Updated farmer ID {farmer_id}")
        return True
    
    def get_farmer(self, farmer_id: int) -> Optional[Dict]:
        """Get farmer by ID"""
        return self.data["farmers"].get(str(farmer_id))
    
    def get_all_farmers(self) -> List[Dict]:
        """Get all farmers"""
        return list(self.data["farmers"].values())
    
    def search_farmers(self, name: str = None, min_age: int = None, max_age: int = None) -> List[Dict]:
        """Search farmers by criteria"""
        farmers = self.get_all_farmers()
        
        if name:
            farmers = [f for f in farmers if name.lower() in f["name"].lower()]
        if min_age is not None:
            farmers = [f for f in farmers if f["age"] >= min_age]
        if max_age is not None:
            farmers = [f for f in farmers if f["age"] <= max_age]
            
        return farmers
    
    def delete_farmer(self, farmer_id: int) -> bool:
        """Delete farmer by ID"""
        farmer_key = str(farmer_id)
        if farmer_key in self.data["farmers"]:
            del self.data["farmers"][farmer_key]
            self._save_data()
            logger.info(f"Deleted farmer ID {farmer_id}")
            return True
        return False

# Initialize database
db = FarmerDatabase()

def get_experience_level(age: int) -> tuple:
    """Determine experience level and coconut type based on age"""
    if age <= 25:
        return "young and enthusiastic", "tender coconuts"
    elif age <= 40:
        return "experienced and skilled", "premium coconuts"
    elif age <= 60:
        return "wise and knowledgeable", "the finest coconuts"
    else:
        return "veteran and master", "golden harvest coconuts"

@app.route('/api/farmer', methods=['POST'])
def register_farmer():
    """
    Register a new coconut farmer
    Expected JSON: {"name": "string", "age": integer}
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            logger.error("No data received")
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get('name', '').strip()
        age = data.get('age')
        
        # Validate name
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters long"}), 400
            
        # Validate age
        if age is None:
            return jsonify({"error": "Age is required"}), 400
            
        try:
            age = int(age)
        except (ValueError, TypeError):
            return jsonify({"error": "Age must be a number"}), 400
            
        if age < 18 or age > 80:
            return jsonify({"error": "Age must be between 18 and 80"}), 400
        
        # Check for duplicate names (case insensitive)
        existing_farmers = db.search_farmers(name=name)
        if existing_farmers:
            return jsonify({
                "error": "Farmer with this name already exists",
                "existing_farmer_id": existing_farmers[0]["id"],
                "suggestion": "Use update endpoint to modify existing record"
            }), 409
        
        # Generate personalized message
        experience, coconut_type = get_experience_level(age)
        greeting = f"Welcome, {name}! At {age} years young, you're {experience} in growing {coconut_type}!"
        
        # Store farmer data
        farmer_data = {
            "name": name,
            "age": age,
            "experience_level": experience,
            "coconut_type": coconut_type
        }
        
        farmer_id = db.add_farmer(farmer_data)
        farmer_record = db.get_farmer(farmer_id)
        
        logger.info(f"New farmer registered: {name}, Age: {age}, ID: {farmer_id}")
        
        return jsonify({
            "status": "success",
            "message": greeting,
            "farmer_id": farmer_id,
            "registration_date": farmer_record["registration_date"],
            "farmer_data": farmer_record
        }), 200
        
    except Exception as e:
        logger.error(f"Error registering farmer: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/farmer/<int:farmer_id>', methods=['PUT'])
def update_farmer(farmer_id):
    """
    Update existing farmer data
    Expected JSON: {"name": "string", "age": integer} (partial updates allowed)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if farmer exists
        existing_farmer = db.get_farmer(farmer_id)
        if not existing_farmer:
            return jsonify({"error": f"Farmer with ID {farmer_id} not found"}), 404
        
        update_data = {}
        
        # Validate and prepare update data
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({"error": "Name cannot be empty"}), 400
            if len(name) < 2:
                return jsonify({"error": "Name must be at least 2 characters long"}), 400
            
            # Check for duplicate names (excluding current farmer)
            existing_farmers = db.search_farmers(name=name)
            if existing_farmers and any(f["id"] != farmer_id for f in existing_farmers):
                return jsonify({"error": "Another farmer with this name already exists"}), 409
            
            update_data["name"] = name
        
        if 'age' in data:
            try:
                age = int(data['age'])
            except (ValueError, TypeError):
                return jsonify({"error": "Age must be a number"}), 400
                
            if age < 18 or age > 80:
                return jsonify({"error": "Age must be between 18 and 80"}), 400
            
            update_data["age"] = age
            # Update experience level based on new age
            experience, coconut_type = get_experience_level(age)
            update_data["experience_level"] = experience
            update_data["coconut_type"] = coconut_type
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Update farmer data
        success = db.update_farmer(farmer_id, update_data)
        if not success:
            return jsonify({"error": "Failed to update farmer"}), 500
        
        updated_farmer = db.get_farmer(farmer_id)
        
        # Generate updated greeting
        experience, coconut_type = get_experience_level(updated_farmer["age"])
        greeting = f"Updated successfully! {updated_farmer['name']}, now {updated_farmer['age']} years, is {experience} in growing {coconut_type}!"
        
        logger.info(f"Updated farmer ID {farmer_id}: {updated_farmer['name']}")
        
        return jsonify({
            "status": "success",
            "message": greeting,
            "farmer_id": farmer_id,
            "last_updated": updated_farmer["last_updated"],
            "farmer_data": updated_farmer
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating farmer {farmer_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/farmer/<int:farmer_id>', methods=['GET'])
def get_farmer(farmer_id):
    """Get specific farmer data"""
    farmer = db.get_farmer(farmer_id)
    if not farmer:
        return jsonify({"error": f"Farmer with ID {farmer_id} not found"}), 404
    
    return jsonify({
        "status": "success",
        "farmer_data": farmer
    }), 200

@app.route('/api/farmers', methods=['GET'])
def get_all_farmers():
    """Get all registered farmers with optional filtering"""
    try:
        name_filter = request.args.get('name', '').strip()
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        
        farmers = db.search_farmers(
            name=name_filter if name_filter else None,
            min_age=min_age,
            max_age=max_age
        )
        
        return jsonify({
            "status": "success",
            "total_farmers": len(farmers),
            "farmers": farmers,
            "filters_applied": {
                "name": name_filter,
                "min_age": min_age,
                "max_age": max_age
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving farmers: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/farmer/<int:farmer_id>', methods=['DELETE'])
def delete_farmer(farmer_id):
    """Delete a farmer record"""
    success = db.delete_farmer(farmer_id)
    if not success:
        return jsonify({"error": f"Farmer with ID {farmer_id} not found"}), 404
    
    return jsonify({
        "status": "success",
        "message": f"Farmer with ID {farmer_id} has been deleted"
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    all_farmers = db.get_all_farmers()
    
    # Initialize default statistics
    stats = {
        "total_farmers": 0,
        "average_age": 0,
        "age_groups": {
            "young": 0,
            "prime": 0,
            "experienced": 0,
            "veteran": 0
        },
        "last_updated": db.data.get("last_updated"),
        "next_available_id": db.data.get("next_id", 1)
    }
    
    if all_farmers:
        total_farmers = len(all_farmers)
        average_age = sum(f["age"] for f in all_farmers) / total_farmers
        
        # Update statistics with actual data
        stats.update({
            "total_farmers": total_farmers,
            "average_age": round(average_age, 1),
            "age_groups": {
                "young": len([f for f in all_farmers if f["age"] <= 25]),
                "prime": len([f for f in all_farmers if f["age"] <= 40]),
                "experienced": len([f for f in all_farmers if f["age"] <= 60]),
                "veteran": len([f for f in all_farmers if f["age"] > 60])
            }
        })
    
    return jsonify({
        "status": "success",
        "statistics": stats
    }), 200

@app.route('/api/greeting', methods=['GET'])
def get_greeting():
    """Return a generic greeting message"""
    total_farmers = len(db.get_all_farmers())
    return jsonify({
        "message": "🌴 Welcome to the Coconut Farmers Community! 🥥",
        "description": f"Join our community of {total_farmers} coconut growers sharing knowledge and resources",
        "total_members": total_farmers
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    total_farmers = len(db.get_all_farmers())
    return jsonify({
        "status": "healthy", 
        "service": "Coconut Farmer API",
        "database": "operational",
        "total_farmers": total_farmers,
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("🌴 Starting Coconut Farmer API Server...")
    print("📍 API endpoints available:")
    print("   POST   /api/farmer              - Register new farmer")
    print("   PUT    /api/farmer/<id>         - Update existing farmer")
    print("   GET    /api/farmer/<id>         - Get specific farmer")
    print("   GET    /api/farmers             - List all farmers (with filters)")
    print("   DELETE /api/farmer/<id>         - Delete farmer")
    print("   GET    /api/stats               - Get statistics")
    print("   GET    /api/greeting            - Get welcome message")
    print("   GET    /api/health              - Health check")
    print(f"💾 Data file: {db.filename}")
    app.run(debug=True, host='0.0.0.0', port=5000)