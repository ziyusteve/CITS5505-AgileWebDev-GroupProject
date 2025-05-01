from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Optional, Length
from flask import current_app

class DatasetUploadForm(FlaskForm):
    title = StringField('球员名称 (可选)', validators=[
        Optional(),
        Length(max=100, message='标题不能超过100个字符')
    ])
    description = TextAreaField('描述 (可选)', validators=[
        Optional(),
        Length(max=500, message='描述不能超过500个字符')
    ])
    file = FileField('上传文本文件', validators=[
        FileRequired(message='请选择一个文件'),
        FileAllowed(['txt', 'docx', 'pdf'], message='只允许上传TXT、DOCX或PDF文件')
    ])
    submit = SubmitField('分析并生成球探报告') 