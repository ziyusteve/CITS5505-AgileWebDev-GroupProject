# Data Analytics Platform

A web application that allows users to upload private data, view automated analysis of their data, and selectively share results with other users. The platform employs modern web technologies to provide an intuitive user interface and powerful data processing capabilities.

## Team Members

| UWA ID   | Name | Github Username         |
|----------|----------|-----------------|
| 24370783   | Ziyu (Steve) Wang       | ziyusteve   |
| 24438869   | Chenxiao Jiang          |Nekoson   |
| 23934529   | Ziqian Qin          | PrescottClub   |
|   |       |   |

## Features

- **User Authentication**: Register, login, and maintain your private data space
- **Data Upload**: Easy upload of data files in various formats (CSV, TXT, XLSX, JSON)
- **Data Visualization**: Automated analysis with interactive visualizations
- **Selective Sharing**: Control who can see your data and analysis results

## Project Architecture

### Directory Structure
```
data_analytics_platform/
│
├── run.py                 # Main Flask application entry point
├── app/                   # Module structure with Blueprint architecture
│   ├── __init__.py        # Application factory function
│   ├── config.py          # Configuration settings
│   ├── extensions.py      # Flask extensions initialization
│   ├── utils.py           # Utility functions
│   ├── api/               # API Blueprint module
│   ├── auth/              # Authentication Blueprint module
│   ├── dashboard/         # Dashboard Blueprint module
│   ├── datasets/          # Datasets Blueprint module
│   ├── main/              # Main/home Blueprint module
│   ├── models/            # Database models
│   ├── sharing/           # Sharing Blueprint module
│   ├── visualization/     # Visualization Blueprint module
│   └── templates/         # HTML templates organized by feature
│       ├── base.html      # Base layout template
│       ├── auth/          # Authentication templates
│       ├── dashboard/     # Dashboard templates
│       ├── datasets/      # Datasets templates
│       ├── main/          # Main/home templates
│       ├── sharing/       # Sharing templates
│       └── visualization/ # Visualization templates
├── requirements.txt       # Python dependency list
├── instance/              # Instance folder containing SQLite database
│   └── site.db            # SQLite database file
├── data/                  # Data storage directory 
│   └── uploads/           # User uploaded data files
├── static/                # Static resources
│   ├── css/               # CSS stylesheets
│   │   └── style.css      # Custom styles
│   ├── images/            # Image resources
│   │   └── data-analytics.svg # Sample data analysis chart
│   └── js/                # JavaScript files
│       └── main.js        # Custom JavaScript functionality
```

## Technology Stack

### Backend Technologies
- **Flask**: Web framework for handling HTTP requests and routing
- **SQLAlchemy**: ORM framework for managing data models and database interactions
- **SQLite**: Lightweight relational database for storing user and dataset information
- **Python Libraries**: Data processing and analysis using the following libraries:
  - Pandas (2.2.3): For data manipulation and analysis, compatible with Python 3.12
  - NumPy (1.26.0): For mathematical computations
  - Plotly (5.17.0): For interactive data visualization and analysis

### Frontend Technologies
- **HTML5/CSS3**: Page structure and styling
- **Bootstrap**: Responsive design framework
- **jQuery**: JavaScript library for simplifying DOM manipulation
- **Plotly.js**: Interactive data visualization library
- **Font Awesome**: Icon library

### Security
- **Authentication**: Flask session management with secure password hashing
- **Access Control**: Permission-based data access and sharing mechanism

## Data Models

The application uses SQLAlchemy to define three main data models:

1. **User Model**:
   - Stores user information: username, email, hashed password
   - Maintains a one-to-many relationship with the Dataset model

2. **Dataset Model**:
   - Stores dataset information: title, upload date, file path, description
   - Has a foreign key relationship with the User model
   - Maintains a one-to-many relationship with the Share model

3. **Share Model**:
   - Manages data sharing between users
   - Contains dataset ID, shared user ID, and sharing date

## Application Workflow

1. **User Authentication Workflow**:
   - New user registration (username, email, password)
   - Password hashing using Werkzeug's security module
   - Login authentication and session creation
   - User state management using Flask sessions

2. **Data Upload Workflow**:
   - User authentication verification
   - User form submission with data file upload (supports CSV, TXT, XLSX, JSON formats)
   - Backend validation of file type and security
   - Generation of unique filenames and file saving
   - Dataset record creation in the database

3. **Data Analysis Workflow**:
   - Loading user data using specialized functions for different file formats (CSV, Excel, JSON)
   - Processing data dynamically using pandas and numpy libraries
   - Automatic statistical analysis including mean, median, and distribution properties
   - Real-time generation of interactive visualizations based on actual uploaded data
   - API endpoints providing JSON data for frontend visualization
   - Dynamic column selection and chart type switching
   - Automatic generation of data insights and pattern detection

4. **Data Sharing Workflow**:
   - User selection of dataset and target users for sharing
   - Creating sharing records
   - Shared users accessing shared data through their dashboards
   - Owner's ability to revoke sharing permissions at any time

## Requirements

- Python 3.8+
- Flask and related extensions (see requirements.txt)
- Modern web browser with JavaScript enabled

## Installation and Setup

1. Clone the repository or download the source code

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Run the Flask application:
```
python run.py
```

4. Access the application in your web browser at:
```
http://127.0.0.1:5000/
```

## Development Process Details

### 1. Initial Project Setup

The development process begins with creating the basic structure of the Flask application:

```python
# Initialize Flask app with application factory pattern
def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='../static')
    
    # 使用配置类
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    # ... register blueprints ...
    
    return app
```

### 2. Key Technical Implementations

#### File Upload and Processing

```python
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return new_filename
```

- Validating file type security
- Generating unique filenames to prevent overwriting
- Securely saving user uploaded files

#### Data Visualization Implementation

- Frontend using Plotly.js to create interactive charts based on real user data
- Backend API endpoints providing data analysis results in JSON format
- Support for multiple chart types (bar, line, pie, scatter) with dynamic switching
- Dynamic X and Y axis column selection for flexible data exploration
- Automatic statistical calculations displayed alongside visualizations

## Data Privacy and Security

- User passwords are securely hashed before storage using Werkzeug's security module
- Data is stored privately by default, visible only to the uploading user
- Sharing is opt-in and selective, with the ability to revoke access at any time
- Permission-based access control for all data operations

## Future Development Recommendations

### 1. Feature Enhancements

1. **Advanced Data Analysis Capabilities**
   - Integrating NLP (Natural Language Processing) for text data analysis
   - Adding machine learning algorithms for predictive analytics and pattern recognition
   - Implementing anomaly detection and outlier identification
   - Supporting time series forecasting and trend analysis

2. **Extended Data Source Support**
   - Adding API connectors to retrieve external data
   - Supporting real-time data streams
   - Integrating public datasets

3. **Collaboration Features**
   - Adding comments and discussion functionality
   - Implementing collaborative editing capabilities
   - Creating team spaces and permission hierarchies

### 2. Technical Optimizations

1. **Performance Improvements**
   - Implementing data caching mechanisms
   - Optimizing large dataset processing
   - Using asynchronous tasks for long-running analyses

2. **Architecture Improvements**
   - Considering migration to microservices architecture
   - Separating frontend and backend (Flask API + SPA frontend)
   - Adopting containerized deployment (Docker)

3. **Security Enhancements**
   - Implementing stronger authentication (e.g., 2FA)
   - Adding API keys and rate limiting
   - Encrypted data storage

## Development Best Practices

Our team followed these best practices during development:

1. **Code Organization**
   - Implementation of Flask Blueprints for modular code organization
   - Adoption of a feature-based folder structure for better maintainability
   - Clear separation of concerns between data processing, visualization, and user management
   - Creation of reusable components and helper functions

2. **Testing Strategy**
   - Adding unit tests and integration tests
   - Using automated testing to cover key functionalities

3. **Documentation**
   - Adding detailed docstrings in code
   - Creating comprehensive technical documentation
   - Maintaining developer guides

## Conclusion

The development of the Data Analytics Platform combines modern web development technologies with data science tools to create a feature-rich and user-friendly application. By following good software engineering practices and adopting an appropriate technology stack, we have built a system that both meets current needs and can be expanded in the future.
