from app import create_app, db

# Create the app using TestingConfig
app = create_app('testing')

# Optional: Set up test data here
with app.app_context():
    db.create_all()
    print("✅ In-memory test database initialized.")

    # Example: Create a test user
    # from app.models.user import User
    # user = User(username='testuser', email='test@example.com')
    # user.set_password('test123')
    # db.session.add(user)
    # db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)