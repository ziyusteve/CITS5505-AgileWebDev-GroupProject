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
    
    # 注册蓝图 (后续步骤将添加)
    
    return app
