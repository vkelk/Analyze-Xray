import os
import uuid

from flask import jsonify, render_template, request, Markup, flash
from werkzeug.utils import secure_filename, CombinedMultiDict

from app.config import base_config
from app.xray import xray
from .forms import FileForm
from .xrayimage import analyze_image


@xray.route('/', methods=['GET', 'POST'])
@xray.route('/analyzexray', methods=['GET', 'POST'])
def index():
    form = FileForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        f = form.file_input.data
        filename = secure_filename(str(uuid.uuid4())[:8] + f.filename)
        try:
            file_location = os.path.join(
                base_config.UPLOAD_FOLDER, filename
                )
            f.save(file_location)
        except Exception as e:
            message = Markup(
                "<strong>Error!</strong> Could not upload file")
            flash(message, 'warning')
            file_location = None
        return render_template(
            'index.html',
            form=form,
            filename=filename
            )
    """Returns the applications index page."""
    return render_template('index.html', form=form)


@xray.route('/getresult/<filename>', methods=['GET'])
def getresult(filename):
    file_location = os.path.join(base_config.UPLOAD_FOLDER, filename)
    result = analyze_image(file_location)
    data = {}
    if result:
        try:
            data['result'] = result
            data['status'] = 'OK'
        except Exception:
            data['status'] = 'error'
            data['err_message'] = 'Could not extract text from the file'
    else:
        data['status'] = 'error'
        data['err_message'] = 'Incorrect input file format'
    return jsonify(data)


@xray.route('/api/imagefile', methods=['GET', 'POST'])
def imagefile():
    if request.method == 'POST':
        form = FileForm(CombinedMultiDict((request.files, request.form)))
        if form.validate_on_submit():
            data = {}
            f = form.file_input.data
            data['filename'] = f.filename
            filename = secure_filename(str(uuid.uuid4())[:8] + f.filename)
            file_location = os.path.join(
                base_config.UPLOAD_FOLDER, filename
                )
            f.save(file_location)
            result = analyze_image(file_location)
            if result:
                try:
                    data['result'] = result
                    data['status'] = 'OK'
                except Exception:
                    data['status'] = 'error'
                    data['err_msg'] = 'Could not extract text from the file'
            else:
                data['status'] = 'error'
                data['err_message'] = 'Incorrect input file format'
        return jsonify(data)
    return render_template('api_doc.html')
