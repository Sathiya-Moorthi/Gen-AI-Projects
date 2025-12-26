from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def calculate_bmi(height, weight):
    """Calculate BMI and return category"""
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    bmi = round(bmi, 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal" 
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
        
    return bmi, category

@app.route('/calculate-bmi', methods=['POST'])
def bmi_calculator():
    try:
        data = request.get_json()
        
        # Validation
        if not data or 'height' not in data or 'weight' not in data:
            return jsonify({'error': 'Height and weight are required'}), 400
            
        height = float(data['height'])
        weight = float(data['weight'])
        
        if height <= 0 or weight <= 0:
            return jsonify({'error': 'Height and weight must be positive values'}), 400
            
        # Calculate BMI
        bmi, category = calculate_bmi(height, weight)
        
        return jsonify({
            'bmi': bmi,
            'category': category,
            'message': f'Your BMI is {bmi} - {category}'
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid input format'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)