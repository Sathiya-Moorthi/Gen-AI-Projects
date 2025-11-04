def calculate(num1, num2, operation):
    """
    Perform arithmetic operation on two numbers.
    Supported operations: add, subtract, multiply, divide
    """
    try:
        if operation in ["add", "+"]:
            return num1 + num2
        elif operation in ["subtract", "-"]:
            return num1 - num2
        elif operation in ["multiply", "*", "x"]:
            return num1 * num2
        elif operation in ["divide", "/"]:
            if num2 == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return num1 / num2
        else:
            raise ValueError(f"Invalid operation: {operation}")
    except Exception as e:
        return f"Error: {e}"


def read_inputs(file_path):
    """
    Reads multiple input sets from a text file.
    Expected format:
        num1=10
        num2=5
        operation=add
        ---
        num1=8
        num2=0
        operation=divide
        ---
    (Each set is separated by ---)
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()

        # Split multiple blocks using "---"
        blocks = [block.strip() for block in content.split('---') if block.strip()]
        input_sets = []

        for block in blocks:
            data = {}
            for line in block.splitlines():
                if '=' in line:
                    key, value = line.strip().split('=')
                    data[key.strip().lower()] = value.strip().lower()

            num1 = float(data.get('num1'))
            num2 = float(data.get('num2'))
            operation = data.get('operation')
            input_sets.append((num1, num2, operation))

        return input_sets
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file '{file_path}' not found.")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid input format: {e}")


def write_outputs(file_path, results):
    """Writes all results to an output file."""
    try:
        with open(file_path, 'w') as file:
            for i, result in enumerate(results, start=1):
                file.write(f"Operation {i}: {result}\n")
        print(f"✅ All results written to '{file_path}' successfully.")
    except Exception as e:
        print(f"❌ Failed to write output: {e}")


def main():
    input_file = r"D:\Gen AI Projects\venv\Python_scripts\Input_files\input_file.txt"
    output_file = r"D:\Gen AI Projects\venv\Python_scripts\Output_files\output_file.txt"

    try:
        input_sets = read_inputs(input_file)
        results = []

        for i, (num1, num2, operation) in enumerate(input_sets, start=1):
            print(f"➡️ Processing set {i}: {num1}, {num2}, {operation}")
            result = calculate(num1, num2, operation)
            results.append(f"{num1} {operation} {num2} = {result}")

        write_outputs(output_file, results)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
