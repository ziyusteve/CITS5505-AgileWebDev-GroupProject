# Deployment Guide

This document outlines the steps for deploying the Scout Analytics application to various environments.

## Prerequisites
- Python 3.11 or higher
- Git
- SQLite (for development) or PostgreSQL (for production)
- Gemini API access key

## Environment Setup

### Development Environment

1. Clone the repository:
```bash
git clone <repository-url>
cd 5505_group_project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements/dev.txt
```

4. Create a `.env` file from the example:
```bash
cp env.example .env
```
Edit the `.env` file to include your API keys and other configurations. Critical configurations include:
```
# API keys
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration 
MAIL_SERVER=smtp.gmail.com  # or smtp.office365.com for Outlook
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your-email-password-or-app-password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

5. Run database migrations:
```bash
flask db upgrade
```

6. Start the development server:
```bash
python run.py
```

### Production Environment

1. Follow steps 1-4 from the development setup, but use:
```bash
pip install -r requirements.txt
```

2. Configure environment variables for production:
```
SECRET_KEY=<strong-random-key>
FLASK_ENV=production
FLASK_DEBUG=False
GEMINI_API_KEY=<your-api-key>
```

3. Set up a production-grade WSGI server:

For Linux/Unix:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

For Windows:
```bash
pip install waitress
waitress-serve --port=8000 "app:create_app('production')"
```

4. Configure a reverse proxy (Nginx/Apache) to handle static files and forward requests to the WSGI server.

## Database Management

### Performing Migrations

When schema changes are made, create and apply migrations:

```bash
# Create a migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback a migration if needed
flask db downgrade
```

### Backup and Restore

Regularly backup your database:

```bash
# For SQLite
cp instance/site.db instance/site.db.backup-$(date +%Y%m%d)

# For PostgreSQL
pg_dump -U username -d database_name > backup_$(date +%Y%m%d).sql
```

## Deployment Process

1. **Prepare Release**:
   - Merge all features to develop branch
   - Test thoroughly
   - Update version number and CHANGELOG.md
   - Create a pull request to main

2. **Tag Release**:
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1 with email verification"
   git push origin v1.0.1
   ```

3. **Monitor Deployment**:
   - Check GitHub Actions CI/CD pipeline
   - Verify the application starts correctly
   - Run health checks

4. **Rollback Procedure** (if needed):
   ```bash
   # Revert to previous tag
   git checkout v1.x.x-1

   # Deploy the previous version
   # Rollback database if necessary
   flask db downgrade
   ```

## Email Service Configuration

### Gmail Configuration
For Gmail email service:
1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" specifically for this application
3. Use the app password in your `.env` file as `MAIL_PASSWORD`

### Outlook Configuration
For Outlook email service:
1. Use your standard email and password
2. Set the following in your `.env` file:
   ```
   MAIL_SERVER=smtp.office365.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_outlook_email@outlook.com
   MAIL_PASSWORD=your_outlook_password
   MAIL_DEFAULT_SENDER=your_outlook_email@outlook.com
   ```

### Testing Email Configuration
Verify your email configuration by running:
```bash
python -m tests.test_email_verification
```

## Health Check and Monitoring

Add a health check endpoint for monitoring services:

```python
@app.route('/health')
def health_check():
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        db_status = 'ok'
    except:
        db_status = 'error'

    return jsonify({
        'status': 'ok',
        'database': db_status,
        'version': 'v1.0.0'
    })
```

Configure your monitoring service to regularly call this endpoint.
