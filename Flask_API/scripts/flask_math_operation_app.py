from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Perform basic math operations using JSON input.
    Example JSON body:
    {
        "operation": "add",
        "num1": 10,
        "num2": 5
    }
    """
    data = request.get_json()

    # Input validation
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if not all(k in data for k in ("operation", "num1", "num2")):
        return jsonify({"error": "Missing one of: operation, num1, num2"}), 400

    operation = data["operation"].lower()
    num1 = data["num1"]
    num2 = data["num2"]

    try:
        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return jsonify({"error": "Division by zero is not allowed"}), 400
            result = num1 / num2
        else:
            return jsonify({"error": "Invalid operation. Use add, subtract, multiply, divide"}), 400

        return jsonify({
            "operation": operation,
            "num1": num1,
            "num2": num2,
            "result": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
