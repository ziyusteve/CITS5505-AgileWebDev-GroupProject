# 5505 Group Project

A Flask-based web application for dataset sharing, visualization, and dashboard analytics.

## Features

- User authentication (login, register, privacy policy, terms of service)
- Interactive dashboard displaying key metrics
- Secure dataset upload and management
- Dataset sharing with customizable permissions
- Data visualization interface (charts, graphs, etc.)
- RESTful API endpoints for integration
- Automated testing suite via `run_testing.py`

## Tech Stack

- Python 3.11
- Flask
- SQLite (via SQLAlchemy)
- Jinja2 templating
- HTML5, CSS3, JavaScript

## Installation

```powershell
# Clone the repository
git clone https://your-repo-url.git
cd 5505_group_project

# Create virtual environment and activate
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements/dev.txt

# Install testing dependencies
pip install -r requirements/test.txt
```

## Configuration

- Application configuration can be found in `app/config.py`.
- Database file located at `instance/site.db` by default.
- You can override settings via environment variables or a custom config.

## Usage

```powershell
# Run the development server
python run.py

# Run application verification
python scripts/check_app.py

# Run tests
python -m pytest tests/
```

- Access the application at http://localhost:5000

## Database Migrations

This application uses Flask-Migrate for database migrations:

```powershell
# Initialize migration repository
flask db init

# Create a migration
flask db migrate -m "Migration message"

# Apply migrations to the database
flask db upgrade

# Rollback the last migration
flask db downgrade
```

## Project Structure

The project is organized as follows:

- `app/`: Main application code
- `data/uploads/`: User uploaded files
- `migrations/`: Database migration files
- `requirements/`: Dependency management
  - `base.txt`: Production dependencies
  - `dev.txt`: Development dependencies
  - `test.txt`: Testing dependencies
- `scripts/`: Utility scripts
- `static/`: Static assets (CSS, JS, images)
- `tests/`: Test files and test data
- `run.py`: Application entry point
- `requirements.txt`: Main requirements file
- `pyproject.toml`: Code formatting and linting configuration
- `CODE_QUALITY.md`: Code quality guidelines

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
