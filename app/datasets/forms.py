from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, Length, ValidationError
from werkzeug.utils import secure_filename


class UploadDatasetForm(FlaskForm):
    """Dataset upload form"""

    title = StringField("Player Name", validators=[Optional(), Length(max=100)])
    file = FileField("Upload File", validators=[FileRequired("Please select a file")])
    submit = SubmitField("Analyze and Generate Scout Report")

    def validate_file(self, field):
        """Validate if the file type is allowed"""
        if field.data:
            # Get file extension
            filename = field.data.filename
            ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

            # Check if extension is in the allowed list
            allowed_extensions = {"csv", "txt", "json", "xlsx", "xls"}
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}'
                )

            # Additional security checks
            try:
                secure_name = secure_filename(filename)
                if not secure_name or secure_name != filename:
                    raise ValidationError("Filename contains invalid characters")
            except Exception:
                # If secure_filename fails (due to dependency issues), skip this check
                pass
