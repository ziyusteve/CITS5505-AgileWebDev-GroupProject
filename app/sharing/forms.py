from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class ShareDatasetForm(FlaskForm):
    dataset_id = SelectField('Dataset', validators=[DataRequired()], coerce=int)
    user_id = SelectField('Share with', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Share')

class RevokeShareForm(FlaskForm):
    submit = SubmitField('Revoke') 