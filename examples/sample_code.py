# Example Python file for testing the analyzer

def calculate_sum(numbers):
    result = 0
    for num in numbers:
        result += num
    return result

def process_data(data):
    try:
        return data * 2
    except:  # Bare except - will be flagged
        print("Error occurred")  # Print instead of logging - will be flagged
        return None

password = "admin123"  # Hardcoded secret - will be flagged

class MyClass:
    def VeryLongFunctionName(self):  # Bad naming - will be flagged
        pass
