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
```

## Configuration

- Application configuration can be found in `app/config.py`.
- Database file located at `instance/site.db` by default.
- You can override settings via environment variables or a custom config.

## Usage

```powershell
# Run the development server
python run.py

# Run tests
python run_testing.py
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

```
5505_group_project/
├── app/
│   ├── config.py         # App configuration
│   ├── extensions.py     # Flask extensions initialization
│   └── utils.py          # Utility functions
├── api/                  # API route definitions
├── auth/                 # Authentication routes
├── dashboard/            # Dashboard routes
├── datasets/             # Dataset upload routes
├── main/                 # Main application routes
├── models/               # SQLAlchemy models (User, Dataset, Share)
├── sharing/              # Dataset sharing routes
├── templates/            # Jinja2 HTML templates
├── visualization/        # Visualization routes
├── static/               # CSS, JavaScript, images
├── data/                 # Uploaded data files
├── instance/             # SQLite database
├── uploads/              # Temporary upload storage
├── run.py                # App entry point
├── run_testing.py        # Test runner
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
