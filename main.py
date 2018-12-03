import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename
import xml.etree.ElementTree as ET
import re

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['xml'])

# Global Variables
storage_file_name = 'ParsedData.txt'
delimiter = '|||'

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

    if os.path.exists(storage_file_name):
        write_flag = 'a'
    else:
        write_flag = 'w'

    storage_file = open(storage_file_name, write_flag)
    storage_file.write(fname)
    storage_file.close()

    # Removes instances of 'None' from the text
    relevantText[:] = [x for x in relevantText if x != 'None']
    text_search(relevantText)
    print(relevantText)


def def_description(def_text, text):
    # Finds the name of the defendant, and puts all of the parts of it into a list, to be cleaned up
    # and put into a string later in the function
    sizeoftext = len(text)
    def_name = list()
    innerbreak = False
    outbreak = False
    for i in def_text:
        if len(def_text[i]) < 25:
            j = i
            while j >= 0:
                # Can split into elif tree if bugs are discovered
                if re.search('vs', text[j]) or re.search('v\.', text[j]):
                    k = j + 1
                    while k < sizeoftext:
                        def_name.append(text[k])
                        if re.search('inclusive', text[k]):
                            innerbreak = True
                            break

                        k = k + 1

                if innerbreak:
                    outbreak = True
                    break

                j = j - 1

        if outbreak:
            break

    # Removes formatting form while maintaining text itself
    # Did it in this extensive if else tree in order to insure that I was only removing formatting, and never letters
    # from within the word. Probably a better way to do this, but this way is more secure than the others that I tried
    mod_def_name = list()
    for i in def_name:

        if re.search('\s\s.*?j', i):
            mod_def_name.append(re.sub('\s\s*?j', '', i))
        elif re.search('\s\s\s.*?j', i):
            mod_def_name.append(re.sub('\s\s\s*?j', '', i))
        elif re.search('\s\s.*?i', i):
            mod_def_name.append(re.sub('\s\s*?i', '', i))
        elif re.search('\s\s\s.*?i', i):
            mod_def_name.append(re.sub('\s\s\s*?i', '', i))
        elif re.search('\s.*?\)', i):
            mod_def_name.append(re.sub('\s*?\)', '', i))
        elif re.search('\s\s.*?\|', i):
            mod_def_name.append(re.sub('\s\s.*?\|', '', i))
        elif re.search('\s\s\s.*?\|', i):
            mod_def_name.append(re.sub('\s\s\s.*?\|', '', i))
        else:
            mod_def_name.append(i)

    return " ".join(mod_def_name)


def plaint_description(plaint_text, text):
    sizeoftext = len(text)
    plaint_name = list()
    innerbreak = False
    outbreak = False
    for i in plaint_text:
        if len(plaint_text[i]) < 25:
            j = i
            while j < sizeoftext:
                # Can split into elif tree if bugs are discovered
                if re.search('vs', text[j]) or re.search('v\.', text[j]):
                    k = j - 1
                    while k >= 0:
                        if re.search('Plaintiff', text[k]):
                            plaint_name.append(text[k - 1])
                            innerbreak = True
                            break

                        k = k - 1

                if innerbreak:
                    outbreak = True
                    break

                j = j + 1

        if outbreak:
            break

    # Removes formatting form while maintaining text itself
    # Did it in this extensive if else tree in order to insure that I was only removing formatting, and not effecting
    # the integrity of the string. Probably a better way to do this, but this way is more
    # secure than the others that I tried
    mod_plaint_name = list()
    for i in plaint_name:

        if re.search('\s\s.*?j', i):
            mod_plaint_name.append(re.sub('\s\s*?j', '', i))
        elif re.search('\s\s\s.*?j', i):
            mod_plaint_name.append(re.sub('\s\s\s*?j', '', i))
        elif re.search('\s\s.*?i', i):
            mod_plaint_name.append(re.sub('\s\s*?i', '', i))
        elif re.search('\s\s\s.*?i', i):
            mod_plaint_name.append(re.sub('\s\s\s*?i', '', i))
        elif re.search('\s.*?\)', i):
            mod_plaint_name.append(re.sub('\s*?\)', '', i))
        elif re.search('\s\s.*?\|', i):
            mod_plaint_name.append(re.sub('\s\s.*?\|', '', i))
        elif re.search('\s\s\s.*?\|', i):
            mod_plaint_name.append(re.sub('\s\s\s.*?\|', '', i))
        else:
            mod_plaint_name.append(i)

    return " ".join(mod_plaint_name)


def text_search(text):
    plaint_text = {}
    def_text = {}
    i = 0
    storage_file = open(storage_file_name, "a")

    # Iterates through the text of the doc and finds all occurances of 'Defendant' and 'Plaintiff'
    # Stores these in two dictionaries, with the key being their location in the text list
    for line in text:

        if re.search('Plaintiff', line):
            plaint_text[i] = line
            # print(str(i) + '. ' + line)
        elif re.search('Defendant', line):
            def_text[i] = line

        i = i + 1

    plaint_string = plaint_description(plaint_text, text)

    # This was added specifically for B.xml, it will only be entered when the 'No.' ends up in the same
    # XML text string as the plaintiffs, and is here to handle this fringe case
    # If similar issues arise, this can be expanded into its own function that worries about handling fringe
    # formatting cases
    if re.search('No\.', plaint_string):
        plaint_string = re.sub('No\.', '', plaint_string)

    def_string = def_description(def_text, text)

    storage_file.write(delimiter + plaint_string)
    storage_file.write(delimiter + def_string)
    storage_file.write("\n")

    storage_file.close()


# Currently only allows the upload of one file
# Need to reload page with success description
# Need to define function to then parse data and store in sql db of some sort
#  - Possibly SQLLite?
@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        if request.form['button'] == 'Go to uploader':
            return redirect(url_for('upload_file'))
        elif request.form['button'] == 'Query':
            return redirect(url_for('query_page'))
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            f.save(secure_filename(f.filename))
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            xml_parse(fname)
            os.remove(fname)
            return redirect(url_for('up_success'))
    return render_template('upload.html')


@app.route('/success', methods=['GET', 'POST'])
def up_success():
    if request.method == 'POST':
        return redirect(url_for('home_page'))
    return render_template('upload_success.html')


@app.route('/query', methods=['GET', 'POST'])
def query_page():
    if request.method == 'POST':
        if request.form['button'] == 'Return to Home':
            return redirect(url_for('home_page'))
        elif request.form['button'] == 'Display Parsed XML Data':
            return redirect(url_for('display_data'))
        elif request.form['button'] == 'Clear Stored data':
            os.remove(storage_file_name)
    return render_template('query.html')


# The following code allows me to display the data stored in ParsedData.txt in an easily readable html table
# It is a heavily inspired from the following stack exchange post, and was simply modified for usage in this web app
# https://stackoverflow.com/questions/37174190/what-is-the-proper-way-to-read-a-text-file-and-display-in-html-via-flask-python/37174666
@app.route('/data', methods=['GET', 'POST'])
def display_data():
    if request.method == 'POST':
        if request.form['button'] == 'Return to Home':
            return redirect(url_for('home_page'))
    if not os.path.exists(storage_file_name):
        return render_template('data_display.html', data_points=0, data_history='')
    with open(storage_file_name) as data:
        data_lines = data.readlines()
        data_history = []
        data_points = len(data_lines)

        for i in range(data_points):
            data_history.append(data_lines[i].split(delimiter))
    return render_template('data_display.html', data_points=data_points, data_history=data_history)


if __name__ == '__main__':
    app.run(debug=True)
