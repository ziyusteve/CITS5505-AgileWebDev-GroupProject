# Data Analytics Platform

A web application that allows users to upload private data, view automated analysis of their data, and selectively share results with other users.

## Team Members

| UWA ID   | Name | Github Username         |
|----------|----------|-----------------|
| 24370783   | Ziyu (Steve) Wang       | ziyusteve   |
| 24438869   | Chenxiao Jiang          |Nekoson   |
|   |       |   |
|   |       |   |

## Features

- **User Authentication**: Register, login, and maintain your private data space
- **Data Upload**: Easy upload of data files in various formats (CSV, TXT, XLSX, JSON)
- **Data Visualization**: Automated analysis with interactive visualizations
- **Selective Sharing**: Control who can see your data and analysis results

## Project Structure

```
data_analytics_platform/
│
├── app.py                 # Main Flask application file
├── requirements.txt       # Python dependencies
├── static/               
│   ├── css/               # Stylesheets
│   │   └── style.css     
│   ├── images/            # Images and graphics
│   │   └── data-analytics.svg
│   └── js/                # JavaScript files
│       └── main.js
├── templates/             # HTML templates
│   ├── dashboard.html     # User dashboard view
│   ├── index.html         # Homepage/introduction view
│   ├── layout.html        # Base template
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── share.html         # Data sharing view
│   ├── upload.html        # Data upload view
│   └── visualize.html     # Data visualization view
└── uploads/               # Directory for user uploaded files
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Data Visualization**: Plotly.js
- **Authentication**: Flask session management with secure password hashing

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
python app.py
```

4. Access the application in your web browser at:
```
http://127.0.0.1:5000/
```

## Data Privacy and Security

- User passwords are securely hashed before storage
- Data is stored privately by default, visible only to the uploading user
- Sharing is opt-in and selective, with the ability to revoke access at any time

## Potential Extensions

- Add advanced data analysis algorithms
- Support for more complex data visualization options
- Implement collaborative features for teams working on the same datasets
- Add API functionality to integrate with other services
