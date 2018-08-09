from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from wtforms import SubmitField


class FileForm(FlaskForm):
    file_input = FileField('image_file', validators=[FileRequired()])
    submit = SubmitField('Analyze file')
