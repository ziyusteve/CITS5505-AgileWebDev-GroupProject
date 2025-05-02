from app import create_app

app = create_app()

if __name__ == '__main__':
    # Disable auto-reloader to ensure only one process loads the latest code
    app.run(debug=True, use_reloader=False)
