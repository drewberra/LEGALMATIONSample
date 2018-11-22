import os
from flask import Flask, render_template, request
from werkzeug import secure_filename
import xml.etree.ElementTree as ET
import re

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['xml'])

# TODO: Parse out desirable data correctly (specified below)
# TODO: store data in sql lite db
# TODO: create homepage that gives option to upload file or query database
# TODO: See FIXME in text_search and do same operation for plaintiff

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Currently prints out all text in xml file, including non if no text present
# use this logic to find all instances of 'defendant', 'defendants', and 'plaintiff'
# and then search in this area to find the names of them
# After this point we can store them in an sqllite db that can later to be queried
def xml_parse(fname):
    tree = ET.parse(fname)
    relevantText = list()
    for elem in tree.getiterator():
        if len(str(elem.text)) > 1:
            relevantText.append(str(elem.text))

    # Removes instances of 'None' from the text
    relevantText[:] = [x for x in relevantText if x != 'None']
    text_search(relevantText)
    print(relevantText)


def text_search(text):
    plaint_text = {}
    def_text = {}
    i = 0
    sizeoftext = len(text)
    # Iterates through the text of the doc and finds all occurances of 'Defendant' and 'Plaintiff'
    # Stores these in two dictionaries, with the key being their location in the text list
    for line in text:

        if re.search('Plaintiff', line):
            plaint_text[i] = line
            # print(str(i) + '. ' + line)
        elif re.search('Defendant', line):
            def_text[i] = line

        i = i + 1

    # Finds the name of the defendant, and puts all of the parts of it into a list, to be cleaned up
    # and put into a string later in the function
    # FIXME: This only works for A.xml right now, need to extend to work for B.xml and C.xml so it works for most cases
    def_name = list()
    innerbreak = False
    outbreak = False
    for i in def_text:
        if len(def_text[i]) < 14:
            j = i
            while j >= 0:
                if re.search('vs', text[j]) or re.search("v.", text[j]):
                    k = j
                    while k < sizeoftext:
                        def_name.append(text[k])
                        if re.search('DOES', text[k]):
                            innerbreak = True
                            break

                        k = k + 1

                if innerbreak:
                    outbreak = True
                    break

                j = j - 1

        if outbreak:
            break

    print(def_name)
    print(plaint_text)
    print(def_text)


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