from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class ShareDatasetForm(FlaskForm):
    dataset_id = SelectField('数据集', validators=[DataRequired()], coerce=int)
    user_id = SelectField('共享给', validators=[DataRequired()], coerce=int)
    submit = SubmitField('共享')

class RevokeShareForm(FlaskForm):
    submit = SubmitField('撤销') 