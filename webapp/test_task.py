from celery_config import celery, add_together

def test_add_together(a, b):
    print(f"Sending task to add {a} and {b}")
    result = add_together.delay(a, b)
    # Get the result with a timeout to handle potential hangups
    try:
        print(f"Task result: {result.get(timeout=10)}")  # Adjust timeout as necessary
    except Exception as e:
        print(f"Error fetching result: {e}")

if __name__ == '__main__':
    # You can change these values or parameterize them to test different inputs
    test_add_together(10, 20)
