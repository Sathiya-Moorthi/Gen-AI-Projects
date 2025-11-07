# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow Streamlit to call Flask API

@app.route('/')
def home():
    return "Flask Math API is running!"

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        # Get query parameters
        a = float(request.args.get('a'))
        b = float(request.args.get('b'))
        operation = request.args.get('operation').lower()

        # Perform operation
        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                return jsonify({"error": "Division by zero is not allowed"}), 400
            result = a / b
        elif operation == 'modulus':
            result = a % b
        elif operation == 'power':
            result = a ** b
        else:
            return jsonify({"error": "Invalid operation"}), 400

        return jsonify({
            "a": a,
            "b": b,
            "operation": operation,
            "result": result,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
