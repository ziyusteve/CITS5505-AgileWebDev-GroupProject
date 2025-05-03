import os
import secrets

class Config:
    """基础配置类"""
    # 使用环境变量获取密钥，如果没有则生成一个强随机密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'data/uploads'
    ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'json', 'pdf', 'docx'}
    
    # 球探报告分析配置
    ENABLE_SCOUT_ANALYSIS = True  # 是否启用球探报告分析功能
    ENABLE_SCOUT_DEEP_ANALYSIS = False  # 是否启用基于Transformer的深度分析
    SCOUT_REPORT_EXTENSIONS = {'txt', 'pdf', 'docx'}  # 球探报告支持的文件格式
    
    # API 密钥配置 - 从环境变量读取
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    @classmethod
    def validate_config(cls):
        """验证关键配置是否存在，确保应用能够正常运行"""
        missing_configs = []
        
        if not cls.GEMINI_API_KEY:
            missing_configs.append('GEMINI_API_KEY')
        
        if missing_configs:
            import logging
            logging.warning(f"警告: 缺少关键配置: {', '.join(missing_configs)}。某些功能可能无法正常工作。")
            return False
        return True
    
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 开发环境也使用随机密钥，确保安全性
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境必须使用环境变量中的强密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 如果没有设置环境变量，生成一个警告并使用随机密钥（不推荐用于实际生产）
    if not SECRET_KEY:
        import logging
        logging.warning("警告: 生产环境中未设置SECRET_KEY环境变量。已生成临时随机密钥，但这不适合长期使用。")
        SECRET_KEY = secrets.token_hex(32)

# 配置映射，用于选择不同环境
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
