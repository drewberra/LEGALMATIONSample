import os
from flask import Flask, render_template, request
from werkzeug import secure_filename
import xml.etree.ElementTree as ET

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['xml'])

# TODO: Parse out desirable data correctly (specified below)
# TODO: store data in sql lite db
# TODO: create homepage that gives option to upload file or query database

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# curently prints out all text in xml file, including non if no text present
# use this logic to find all instances of 'defendant', 'defendants', and 'plaintiff'
# and then search in this area to find the names of them
# After this point we can store them in an sqllite db that can later to be queried
def xml_parse(fname):
    tree = ET.parse(fname)
    for elem in tree.getiterator():
        print(elem.text)


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
            xml_parse(fname)
            return 'file uploaded successfully'
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)