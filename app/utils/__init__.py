# 初始化 app/utils 包
# 这个文件使 app/utils 目录成为一个 Python 包，可以被导入

import os
import uuid
import pandas as pd

def allowed_file(filename, allowed_extensions):
    """检查文件是否有允许的扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """生成唯一的文件名，同时保留原始扩展名"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return new_filename

def load_dataset(file_path):
    """根据文件扩展名加载数据集"""
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    try:
        if ext == 'csv':
            df = pd.read_csv(file_path)
        elif ext == 'xlsx':
            df = pd.read_excel(file_path)
        elif ext == 'json':
            df = pd.read_json(file_path)
        elif ext == 'txt':
            # 尝试检测分隔符
            df = pd.read_csv(file_path, sep=None, engine='python')
        else:
            return None, "不支持的文件格式"
        return df, None
    except Exception as e:
        return None, f"加载数据集时出错: {str(e)}" 