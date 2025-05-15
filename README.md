## Purpose of 5505 Group Project - Scout Analysis

**Scout Analytics** is a Flask-based web application designed to empower basketball coaches, scouts, and analysts with tools for efficient dataset management, insightful data visualization, and AI-driven scout report analysis. The primary goal of this application is to streamline the scouting process, allowing users to easily upload player statistics, share datasets securely with team members, visualize performance metrics through interactive dashboards, and leverage artificial intelligence to gain deeper insights from textual scout reports.

The application is built with a modular architecture, utilizing Flask blueprints to organize different functionalities such as user authentication, data handling, and analytics. This design promotes separation of concerns and makes the codebase more manageable and extensible. Key design considerations include a user-friendly interface for intuitive navigation, robust security measures for data protection (including email verification and secure dataset sharing), and a flexible backend capable of integrating various data sources and analytical tools. It aims to be a comprehensive platform for basketball analytics, facilitating data-driven decision-making in player recruitment and development.

A Flask-based web application for dataset sharing, visualization, and dashboard analytics.

## Group Members

| UWA ID   | Name                   | GitHub Username |
|----------|------------------------|-----------------|
| 23934529 | Terence (Ziqian) Qin   | PrescottClub    |
| 24370783 | Steve (Ziyu) Wang      | ziyusteve       |
| 24438869 | CHENXIAO Jiang         | nekoson         |
| 24644061 | Kundan Kumar Jha       | Xoosk           |

## Features

- User authentication (login, register, privacy policy, terms of service)
- Email verification system for increased security
- Interactive dashboard displaying key metrics
- Secure dataset upload and management
- Dataset sharing with customizable permissions
- Data visualization interface (charts, graphs, etc.)
- Scout report analysis with AI integration
- RESTful API endpoints for integration
- Comprehensive automated testing suite

## Tech Stack

- Python 3.11
- Flask
- SQLite (via SQLAlchemy)
- Jinja2 templating
- HTML5, CSS3, JavaScript

## Installation and Setup

- Git and Python should be installed. Some commands:
`sudo apt update`
`sudo apt install git -y`
`sudo apt install python3 python3-pip python3-venv -y`

- Clone the repository (or download and extract the zip file), Github personal access token should be used when github is asking for the username and password.
`git clone https://github.com/ziyusteve/CITS5505-AgileWebDev-GroupProject`
`cd CITS5505-AgileWebDev-GroupProject`

- Create virtual environment and activate it:
`python -m venv venv`
`.\venv\Scripts\Activate.ps1`  # On Windows
`source venv/bin/activate`   # On MacOS/Linux

- Install all required dependencies:
`pip install -r requirements.txt`

#### Configuration

- Application configuration can be found in `app/config.py`.
- Database file located at `instance/site.db` by default.
- You can override settings via environment variables (using format of env.example in .env) or a custom config.

#### Running the Application

- Initialize the database (if not already present):
`flask db upgrade`

- Run the development server
`python run.py`

- Access the application at http://localhost:5000

#### Running Tests

- Run all tests
`python -m pytest tests/`

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
- `CODE_QUALITY.md`: Code quality guidelines (See [Code Quality Guidelines](CODE_QUALITY.md) for more details).
- `DEPLOYMENT.md`: Guide for deploying the application (See [Deployment Guide](DEPLOYMENT.md) for more details).

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
