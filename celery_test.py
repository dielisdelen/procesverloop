from minimal_app import add_together

# Now, enqueue the task
result = add_together.delay(23, 42)

# To wait for and retrieve the result
print('Result:', result.get(timeout=10))
