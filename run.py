"""
Entry point for the Data Analytics Platform
"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
