# Code Quality Guidelines

This project uses the following tools to ensure code quality:

## Installing Development Dependencies

```bash
pip install -r dev-requirements.txt
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
