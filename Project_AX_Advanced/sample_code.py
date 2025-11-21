
def calculate_sum(a, b):
    return a + b

def calculate_product(a, b):
    return a * b

def process_numbers(x, y):
    sum_result = calculate_sum(x, y)
    product_result = calculate_product(x, y)
    return sum_result, product_result

def main():
    result = process_numbers(5, 10)
    print(f"Results: {result}")
