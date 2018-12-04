## Drew Berra's LEGALMATION Coding Challenge
Thank you for the opportunity to work on this assessment, it has beem a pleasure 
and I hope you are happy with the work and skills that I have demonstrated here.

### Imports Used
I completed this project using Python/Flask, and thusly imported several modules 
from Flask and other packages which need to be installed. You can do this by either 
using `pip install` and individually installing all of the packages laid out below (Flask, Flask-RESTFul, etc.) or 
you can use `pip install -r requirements.txt`.

In order to make the installation of the required modules and packages easy, i used
`pip freeze` to list all of my install libraries and their dependencies in `requirements.txt`.
So in order to ensure that the application is running in the intended environment and functioning properly,
create a new virtual environment for the program, and then do `pip install -r
requirements.txt` if you choose to use this method over installing the packages individually.
##### Modules From flask Package:
* Flask
* render_template
* request
* redirect
* url_for
* jsonify

##### Modules From flask_restful Package:
* Api
* Resource
* reqparse

##### Modules From werkzeug Package:
* secure_filename

##### Other Imported Packages:
* xml.etree.ElementTree _as_ ET
* atexit
* re

### Running the python app
This app was built to be used with the above modules and packages, to be run on python3.6, and was made to
work on Ubuntu 18.04. This application should work on other systems if the libraries are all
installed properly, but it needs to be run an at least python 3.6 as it was not tested using any previous versions.
 
Once everything is properly installed, run `python3.6 main.py` from within your virtual environment 
to launch the application. You can then view and interact with the html interface that I created by going to
http://127.0.0.1:5000/. This should also be displayed in your terminal when the program is running.
From here you will be able to upload .xml files which will be properly parsed and subsequently stored. The parsed
information will be stored in two places, it will be stored in a .txt file that is used to display the information
in an easy to understand table that can be accessed by clicking the `query` button on the homepage. Once on the query page 
you will be able to either view the data, navigate back to the home page or clear all of the stored data. The other
place where the parsed information is stored is within the Rest API.

The information in the Rest API can be viewed by navigating to http://127.0.0.1:5000/api/all. You can
also query by filename by navigating to http://127.0.0.1:5000/file/A.xml if you uploaded the file A.xml and wanted to access that
information for example.

#### Bonus Features
* Does not allow for the same file to uploaded twice
    * In this case an error message will be shown and the option to either
    upload another file, or return to home will be given
* Multiple ways to view file information
* Once files have been successful parsed they are deleted so that they don't
take up extra space
* Server Shutdown on homepage that gives shutting down message and properly closes program
* When server is shutdown the program also deletes text document that is used
to display parsed information in html table
* When the 'Clear Stored Data' button on the query page is pressed, it also clears
the file information in the REST API, that way the HTML table and the Rest API are always in sync

### Closing Remarks

I wanted to thank you for again for the opportunity to apply and to take part in this assessment. If you have 
any questions please feel free to reach out to me through any of the means that I provided in my resume and cover letter.
I look forward to hearing back form you and I hope that we can set up a mutually convenient interview.
