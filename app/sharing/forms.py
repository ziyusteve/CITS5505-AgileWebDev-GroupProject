from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class ShareForm(FlaskForm):
    """Form for sharing datasets"""

    dataset_id = SelectField("Dataset", validators=[DataRequired()], coerce=int)
    user_id = SelectField("Share with", validators=[DataRequired()], coerce=int)
    submit = SubmitField("Share")
