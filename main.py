import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug import secure_filename
import xml.etree.ElementTree as ET
import atexit
import re

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['xml'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

# Global Variables
files = [
    # {
    #     "file": "Example.xml",
    #     "Plaintiffs": "This is where the plaintiff\'s name will be displayed.",
    #     "Defendants": "This is where the defendant\'s name will be displayed."
    # }
]
file_data_points = {}
storage_file_name = 'ParsedData.txt'
delimiter = '|||'


# class that is used to define and interact with REST api is inspired from the example at the following link
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
class DocInfo(Resource):
    def get(self, filename):
        for title in files:
            if filename == title["file"]:
                return title, 200
        return "Document not found", 404

    def post(self, filename):
        parser = reqparse.RequestParser()
        parser.add_argument('Plaintiff')
        parser.add_argument('Defendants')
        arguments = parser.parse_args()

        for title in files:
            if filename == title["file"]:
                return "{} has already been uploaded".format(filename), 400

        title = {
            'file': filename,
            'Plaintiffs': arguments['Plaintiffs'],
            'Defendants': arguments['Defendants']
        }

        files.append(title)
        return title, 201

    def put(self, filename):
        parser = reqparse.RequestParser()
        parser.add_argument('Plaintiffs')
        parser.add_argument('Defendants')
        arguments = parser.parse_args()

        for title in files:
            if filename == title['file']:
                title['Plaintiffs'] = arguments['Plaintiffs']
                title['Defendants'] = arguments['Defendants']
                return title, 200

        title = {
            'file': filename,
            'Plaintiffs': arguments['Plaintiffs'],
            'Defendants': arguments['Defendants']
        }

        files.append(title)
        return title, 201

    def delete(self, filename):
        global files
        files = [title for title in files if title['file'] != filename]
        return "{} was successfully removed.".format(filename), 200


api.add_resource(DocInfo, "/file/<string:filename>")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Parses our xml file, and stores the results in our api and a text file that is used to easily display the parsed data
# on data_display.html
def xml_parse(fname):
    global file_data_points
    global files

    if os.path.exists(storage_file_name):
        write_flag = 'a'
        with open(storage_file_name, 'r') as file_check:
            for line in file_check.readlines():
                if re.search(fname, line):
                    file_check.close()
                    return True

    else:
        write_flag = 'w'

    storage_file = open(storage_file_name, write_flag)
    storage_file.write(fname)
    storage_file.close()

    tree = ET.parse(fname)
    relevantText = list()
    for elem in tree.getiterator():
        if len(str(elem.text)) > 1:
            relevantText.append(str(elem.text))

    file_data_points['file'] = fname

    # Removes instances of 'None' from the text
    relevantText[:] = [x for x in relevantText if x != 'None']
    text_search(relevantText)
    files.append(file_data_points.copy())
    file_data_points.clear()

    return False


def def_description(def_text, text):
    # Finds the name of the defendant, and puts all of the parts of it into a list, to be cleaned up
    # and put into a string later in the function
    sizeoftext = len(text)
    def_name = list()
    innerbreak = False
    outbreak = False

    # Searches for key words that have been observed to bracket the information that we want find
    for i in def_text:
        if len(def_text[i]) < 25:
            j = i
            while j >= 0:
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

    # Searches for key words that have been observed to bracket the information that we want find
    for i in plaint_text:
        if len(plaint_text[i]) < 25:
            j = i
            while j < sizeoftext:
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


# Searches through the text provided to find the starting points for
def text_search(text):
    global file_data_points

    plaint_text = {}
    def_text = {}
    i = 0
    storage_file = open(storage_file_name, "a")

    # Iterates through the text of the doc and finds all occurrences of 'Defendant' and 'Plaintiff'
    # Stores these in two dictionaries, with the key being their location index in text list and the item being
    # the string itself. These are then provided to the plaint_description and def_description along with the text list
    # to find and format the information that we want.
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

    # The plaint_string and def_string that were found are stored in our storage file to be displayed on data_display
    # and then subsequently stored in our API
    storage_file.write(delimiter + plaint_string)
    storage_file.write(delimiter + def_string)
    storage_file.write("\n")
    storage_file.close()

    file_data_points['Plaintiffs'] = plaint_string
    file_data_points['Defendants'] = def_string


# Simple function that removes the file that stores the parsed xml data for easy display on data_display.html
def exit_handler():
    if os.path.exists(storage_file_name):
        os.remove(storage_file_name)


atexit.register(exit_handler)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with Werkzeug Server')
    func()

# Route and code for the homepage
@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        if request.form['button'] == 'Go to uploader':
            return redirect(url_for('upload_file'))
        elif request.form['button'] == 'Query':
            return redirect(url_for('query_page'))
        elif request.form['button'] == 'Shutdown Server':
            shutdown_server()
            return 'Server shutting down...'
    return render_template('index.html')


# Route and code for the xml upload page
# If file has already been uploaded we are sent to file_exists() without the file being parsed or subsequently stored
# If the file is not xml, then the page is just refreshed and nothing is done with the file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            f.save(secure_filename(f.filename))
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            file_state = xml_parse(fname)
            os.remove(fname)
            if file_state:
                return redirect(url_for('file_exists'))
            else:
                return redirect(url_for('up_success'))
    return render_template('upload.html')


# Route and code for successful xml upload
@app.route('/success', methods=['GET', 'POST'])
def up_success():
    if request.method == 'POST':
        return redirect(url_for('home_page'))
    return render_template('upload_success.html')


# Route and code for unsuccessful xml upload due to file having been already uploaded
@app.route('/priorfile', methods=['GET', 'POST'])
def file_exists():
    if request.method == 'POST':
        if request.form['button'] == 'Try another file':
            return redirect(url_for('upload_file'))
        elif request.form['button'] == 'Return to Home':
            return redirect(url_for('home_page'))
    return render_template('upload_failure.html')


# Route and code for our query page that allows users to see a graphical interface of the parsed data or clear the data
# that has been stored in both the file and our API
@app.route('/query', methods=['GET', 'POST'])
def query_page():
    if request.method == 'POST':
        if request.form['button'] == 'Return to Home':
            return redirect(url_for('home_page'))
        elif request.form['button'] == 'Display Parsed XML Data':
            return redirect(url_for('display_data'))
        elif request.form['button'] == 'Clear Stored data':
            global files
            if os.path.exists(storage_file_name):
                os.remove(storage_file_name)
                files = []
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


# The following is the route that allows us to view the full API
@app.route('/api/all', methods=['GET'])
def display_api():
    return jsonify(files)


if __name__ == '__main__':
    app.run()
