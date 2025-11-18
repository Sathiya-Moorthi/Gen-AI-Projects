"""
app.py

Flask API backend for the Unit Conversion Application.
Exposes a single /convert endpoint that uses the ConversionLogic module
to perform calculations. Designed for containerization and high reliability.
"""

from flask import Flask, request, jsonify
from conversion_logic import ConversionLogic # Import our core logic

# --- Configuration ---
app = Flask(__name__)
# Defined conversions for dynamic mapping
CONVERSION_MAP = {
    "currency": {
        "USD_to_INR": ConversionLogic.usd_to_inr,
        "INR_to_USD": ConversionLogic.inr_to_usd,
    },
    "temperature": {
        "C_to_F": ConversionLogic.celsius_to_fahrenheit,
        "F_to_C": ConversionLogic.fahrenheit_to_celsius,
    },
    "length": {
        "CM_to_INCH": ConversionLogic.cm_to_inch,
        "INCH_to_CM": ConversionLogic.inch_to_cm,
    },
    "weight": {
        "KG_to_LB": ConversionLogic.kg_to_lb,
        "LB_to_KG": ConversionLogic.lb_to_kg,
    },
}

@app.route('/convert', methods=['POST'])
def convert_unit():
    """
    Handles POST requests for unit conversion.
    
    Expects a JSON payload with:
    {
        "unit_type": "currency" | "temperature" | "length" | "weight",
        "direction": "USD_to_INR" | "C_to_F" | ...,
        "value": 100.0
    }
    
    Returns a JSON response with the calculated result or an error message.
    """
    data = request.get_json()

    # 1. Input Validation (API structure)
    required_fields = ['unit_type', 'direction', 'value']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields.",
            "expected_payload": {"unit_type": "...", "direction": "...", "value": 0}
        }), 400

    unit_type = data['unit_type'].lower()
    direction = data['direction']
    value = data['value']
    
    # 2. Check if unit type and direction are supported
    if unit_type not in CONVERSION_MAP or direction not in CONVERSION_MAP.get(unit_type, {}):
        return jsonify({
            "error": "Unsupported unit type or conversion direction.",
            "supported_units": list(CONVERSION_MAP.keys())
        }), 400

    # 3. Delegation to ConversionLogic
    try:
        conversion_function = CONVERSION_MAP[unit_type][direction]
        
        # Execute the conversion logic
        result = conversion_function(value)
        
        # 4. Successful Response
        return jsonify({
            "status": "success",
            "unit_type": unit_type,
            "direction": direction,
            "input_value": value,
            "converted_value": result
        }), 200

    except ValueError as e:
        # 5. Handling ConversionLogic's Input Validation Error
        # This catches non-numeric input passed to the logic module.
        return jsonify({
            "error": "Invalid value provided for conversion.",
            "details": str(e)
        }), 400
        
    except Exception as e:
        # 6. Catch-all for unexpected server errors
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "details": "An unexpected error occurred during processing."
        }), 500


if __name__ == '__main__':
    # Running Flask in debug mode for development. Use a production WSGI server
    # (like Gunicorn) in a real containerized environment.
    app.run(host='0.0.0.0', port=5000, debug=True)