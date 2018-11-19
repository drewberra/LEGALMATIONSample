import os
from flask import Flask, render_template, request
from werkzeug import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['xml'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Currently only allows the upload of one file
# Need to reload page with success description
# Need to define function to then parse data and store in sql db of some sort
#  - Possibly SQLLite?
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            f.save(secure_filename(f.filename))
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            return 'file uploaded successfully'
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)