from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Optional, Length
from flask import current_app

class DatasetUploadForm(FlaskForm):
    title = StringField('Player Name (Optional)', validators=[
        Optional(),
        Length(max=100, message='Title cannot exceed 100 characters')
    ])
    description = TextAreaField('Description (Optional)', validators=[
        Optional(),
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    file = FileField('Upload Text File', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['txt', 'docx', 'pdf'], message='Only TXT, DOCX, or PDF files are allowed')
    ])
    submit = SubmitField('Analyze and Generate Scout Report') 