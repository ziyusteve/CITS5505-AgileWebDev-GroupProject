from flask import Flask
import os
from app.config import config
from app.extensions import db

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
    
    from app.sharing import bp as sharing_bp
    app.register_blueprint(sharing_bp, url_prefix='/share')
    
    return app
