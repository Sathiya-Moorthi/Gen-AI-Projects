from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation', '')
        
        result = None
        
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                return jsonify({
                    'status': 'error',
                    'error': 'Cannot divide by zero'
                }), 400
            result = num1 / num2
        else:
            return jsonify({
                'status': 'error',
                'error': 'Invalid operation'
            }), 400
        
        return jsonify({
            'status': 'success',
            'result': result,
            'operation': operation
        })
    
    except ValueError:
        return jsonify({
            'status': 'error',
            'error': 'Invalid number format'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)