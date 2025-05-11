from flask import Flask
import os
from app.config import config_by_name as config
from app.extensions import db, login_manager, mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import importlib.util


def check_dependencies():
    """检查关键依赖是否已安装"""
    missing_packages = []

    # 检查关键包
    dependencies = [
        ("email_validator", "验证电子邮件必需"),
        ("pandas", "数据处理必需"),
        ("flask_wtf", "表单处理和CSRF保护必需"),
        ("flask_mail", "邮件发送必需"),
    ]

    for package, description in dependencies:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(f"{package} ({description})")

    if missing_packages:
        print("\n警告: 缺少以下关键依赖:")
        for pkg in missing_packages:
            print(f" - {pkg}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt\n")

    return len(missing_packages) == 0


def create_app(config_name="default"):
    # 检查关键依赖
    check_dependencies()

    app = Flask(__name__, template_folder="templates", static_folder="../static")

    # Use configuration class
    app.config.from_object(config[config_name])

    # Validate key configurations
    config_valid = config[config_name].validate_config()
    if not config_valid:
        app.logger.warning(
            "Application configuration validation failed, some features may not work"
        )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Initialize Flask-Migrate
    Migrate(app, db)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    from app.datasets import bp as datasets_bp
    app.register_blueprint(datasets_bp, url_prefix="/datasets")

    from app.visualization import bp as visualization_bp
    app.register_blueprint(visualization_bp, url_prefix="/visualize")

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    # API endpoints typically don't need CSRF protection
    csrf.exempt(api_bp)

    from app.sharing import bp as sharing_bp
    app.register_blueprint(sharing_bp, url_prefix="/share")

    # Initialize scout report analysis module (only initialize service, no route registration)
    if app.config.get("ENABLE_SCOUT_ANALYSIS", False):
        from app.scout_analysis import scout_bp
        app.register_blueprint(scout_bp)  # No URL prefix set
        app.logger.info("Scout analysis module initialized")

    # Ensure all database tables are created in the application context
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models.user import User
        from app.models.dataset import Dataset
        from app.models.share import Share

        # If scout report analysis is enabled, import its models
        if app.config.get("ENABLE_SCOUT_ANALYSIS", False):
            from app.scout_analysis.models import ScoutReportAnalysis

        # Create all tables
        db.create_all()
        app.logger.info("Database tables created successfully")

    # Log file configuration
    import logging
    from logging.handlers import RotatingFileHandler

    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
        "logs/flask.log", maxBytes=10240, backupCount=10, encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Set global encoding to UTF-8
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    return app
