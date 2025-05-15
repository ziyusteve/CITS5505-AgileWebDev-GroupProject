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

`python3 -m venv venv`

`.\venv\Scripts\Activate.ps1`  # On Windows

`source venv/bin/activate`   # On MacOS/Linux

- Install all required dependencies:

`pip install -r requirements.txt`

#### Configuration

- Application configuration can be found in `app/config.py`.
- Database file located at `instance/site.db` by default.
- You can override settings via environment variables (using format of env.example in .env) or a custom config.

#### Running the Application

- Copy env.example file, rename it into .env, fill in keys and email configuration

- Initialize the database (if not already present):
`flask db upgrade`

- Run the development server
`python run.py`

- Access the application at http://localhost:5000

#### Running Tests

- Run unit tests
`pytest tests/test_api.py`

`pytest tests/test_email_verification.py`

`pytest tests/test_mock_analysis.py`

- Run selenium tests

`pytest tests/selenium/run_tests.py`

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

This project was a collaborative effort with contributions from the following developers:

* **Terence (Ziqian) Qin:**
    * Contributed to the initial project setup, database migrations, blueprint structure refactoring, and implementation of core analysis functionalities.
    * Worked on user authentication (Flask-Login), CSRF protection, API endpoint security, and integration with the Gemini API for player analysis.
    * Made significant contributions to frontend UI design and optimization, including theme creation (e.g., Lakers theme, Gemini theme), page layouts, style improvements, and implementation of visualization components.
    * Actively participated in code reviews, managed pull requests, fixed bugs (such as database compatibility and UI display issues), handled dependency management, updated configuration files, and contributed to documentation updates.
    * Implemented key features including file upload with automatic analysis, dynamic data visualization, internationalization support, text extraction, and NLP model loading.

* **Steve (Ziyu) Wang:**
    * Actively involved in numerous code reviews and merging pull requests, ensuring code quality and project progression.
    * Contributed to writing and maintaining unit and Selenium tests, fixed test-related bugs, and ensured test coverage.
    * Handled extensive updates and improvements to the README documentation, including installation guides, usage instructions, and test commands. Also managed project environment configurations (e.g., .env files, requirements files, Python version issues).
    * Participated in implementing the email verification feature and updating related tests. Refactored parts of the codebase to improve readability and maintainability (e.g., eliminating duplicate dependencies, standardizing code style).
    * Made frontend style adjustments (such as background colors, button styles, table styles), fixed some frontend display bugs, and participated in the implementation and optimization of certain UI elements.

* **CHENXIAO Jiang:**
    * Focused on the website's visual design and user experience improvements, including redesigning login/registration pages, enhancing the homepage hero section, improving the navigation bar, handling icons and images, and optimizing CSS styles.
    * Added bar charts to the data visualization section to display specific data and adjusted chart layouts to fit the overall design.
    * Contributed to adding page content (such as coach slogans, review information) and optimizing typography and layout (e.g., fonts, spacing, element positioning).
    * Participated in optimizing some code sections and adding/modifying comments, including translating Chinese comments to English.

* **Kundan Kumar Jha:**
    * Primarily addressed specific code issues, such as indentation errors and translating Chinese comments to English.
    * Contributed to adding Selenium test cases to improve the application's test coverage.
    * Resolved specific UI bugs, for instance, the tab highlighting issue.

## License

This project is licensed under the MIT License.

## References

Below is a list of resources and tools that were consulted or used during the development of this project:

### Documentation and APIs
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Python Documentation](https://docs.python.org/3/)
- [Google Gemini API Documentation](https://ai.google.dev/docs/gemini_api)
- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/en/latest/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/en/stable/)
- [Flask-Cors Documentation](https://flask-cors.readthedocs.io/en/latest/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/en/latest/)
- [Flask-Bcrypt Documentation](https://flask-bcrypt.readthedocs.io/en/latest/)
- [Flask-Debug Toolbar Documentation](https://flask-debugtoolbar.readthedocs.io/en/latest/)
- [Flask-Script Documentation](https://flask-script.readthedocs.io/en/latest/)
- [Flask-Testing Documentation](https://flask-testing.readthedocs.io/en/latest/)
- [Flask-Selenium Documentation](https://flask-selenium.readthedocs.io/en/latest/)
- [Flask-RESTful Documentation](https://flask-restful.readthedocs.io/en/latest/)
- [Flask-RESTPlus Documentation](https://flask-restplus.readthedocs.io/en/stable/)

### Articles and Tutorials

### AI Assistance
- **GitHub Copilot**: Used for code completion, generating boilerplate code, and assisting with debugging.

### Other Resources
- [Stack Overflow](https://stackoverflow.com/) for specific programming questions
- [GitHub Discussions](https://github.com/) for community support and collaboration