# Code Quality Guidelines

This project uses the following tools to ensure code quality:

## Installing Development Dependencies

```bash
pip install -r requirements/dev.txt
```

## Code Formatting Tools

### Black

Run the following command to format code:

```bash
black app/
```

### Flake8

Run the following command to check code style:

```bash
flake8 app/
```

## Pre-commit Hooks

This project uses pre-commit to automatically run formatting and code checks.

Install pre-commit hooks:

```bash
pre-commit install
```

Pre-commit hooks will run automatically before each commit, ensuring code compliance.

## Testing Guidelines

### Unit Tests

All new features should be covered by unit tests. These tests should:

1. Be located in the `tests` directory
2. Follow the unittest framework conventions
3. Include assertions for both expected and edge cases
4. Validate response structures, data types, and values

Run tests with:

```bash
python -m tests.run_testing
```

### Test Coverage

Aim for at least 80% test coverage for all new code. Check coverage using:

```bash
coverage run -m tests.run_testing
coverage report
```

## Pull Request Guidelines

Before submitting a pull request:

1. Run all automated tests
2. Update relevant documentation
3. Format code with Black
4. Run Flake8 and fix any issues
5. Ensure any new feature has proper unit tests

## Code Documentation Standards

Please follow these documentation standards:

1. Add PEP 257 compliant docstrings to all functions and classes
2. Documentation should include:
   - Function description
   - Parameter descriptions
   - Return value descriptions
   - Exception descriptions (if applicable)

For example:

```python
def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Args:
        numbers (list): List of numbers

    Returns:
        float: The average value

    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Number list cannot be empty")
    return sum(numbers) / len(numbers)
```
