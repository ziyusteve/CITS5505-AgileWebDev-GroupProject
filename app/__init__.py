from flask import Flask
import os
from app.config import config
from app.extensions import db, login_manager
from flask_wtf.csrf import CSRFProtect

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='../static')
    
    # 使用配置类
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 初始化CSRF保护
    csrf = CSRFProtect(app)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.datasets import bp as datasets_bp
    app.register_blueprint(datasets_bp, url_prefix='/datasets')
    
    from app.visualization import bp as visualization_bp
    app.register_blueprint(visualization_bp, url_prefix='/visualize')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    # API端点通常不需要CSRF保护
    csrf.exempt(api_bp)
    
    from app.sharing import bp as sharing_bp
    app.register_blueprint(sharing_bp, url_prefix='/share')
      # 初始化球探报告分析模块（不注册路由，只初始化服务）
    if app.config.get('ENABLE_SCOUT_ANALYSIS', False):
        from app.scout_analysis import scout_bp
        app.register_blueprint(scout_bp)  # 不设置URL前缀
        app.logger.info("Scout analysis module initialized")
    
    # 确保在应用上下文中创建所有数据库表
    # 首先导入所有模型，然后一次性创建所有表
    with app.app_context():
        # 先导入所有模型
        from app.models.user import User
        from app.models.dataset import Dataset
        from app.models.share import Share
        
        # 如果启用了球探报告分析，再导入其模型
        if app.config.get('ENABLE_SCOUT_ANALYSIS', False):
            from app.scout_analysis.models import ScoutReportAnalysis
              # 创建所有表
        db.create_all()
        app.logger.info("Database tables for scout analysis created if not exists")
    
    # 日志文件配置
    import logging
    from logging.handlers import RotatingFileHandler
    import codecs
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flask.log', maxBytes=10240, backupCount=10, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # 设置全局编码为UTF-8
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    return app
