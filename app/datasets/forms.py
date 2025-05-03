from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from flask import current_app
import os

class UploadDatasetForm(FlaskForm):
    """数据集上传表单"""
    title = StringField('球员名称', validators=[Optional(), Length(max=100)])
    file = FileField('上传文件', validators=[
        FileRequired('请选择一个文件')
    ])
    submit = SubmitField('分析并生成球探报告')
    
    def validate_file(self, field):
        """验证文件类型是否被允许"""
        if field.data:
            # 获取文件扩展名
            filename = field.data.filename
            ext = os.path.splitext(filename)[1][1:].lower()
            # 检查扩展名是否在允许列表中
            if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                raise ValidationError('不支持的文件类型') 