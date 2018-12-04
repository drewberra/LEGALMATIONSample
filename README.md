## Drew Berra's LEGALMATION Coding Challenge
Thank you for the opportunity to work on this assessment, it has beem a pleasure 
and I hope you are happy with the work and skills that I have demonstrated here.

###Imports Used
I completed this project using Python/Flask, and thusly imported several modules 
from the Flask package that need to be which need to be installed using `pip install`
#####Modules From flask Package:
* Flask
* render_template
* request
* redirect
* url_for
* jsonify

#####Modules From flask_restful Package:
* Api
* Resource
* reqparse

#####Modules From werkzeug Package:
* secure_filename

#####Other Imported Packages:
* xml.etree.ElementTree _as_ ET
* atexit
* re

###Running the python app
This app was built to be used with the above modules and packages, to be run on python3.6, and was made to
work on Ubuntu 18.04. This application should work on other systems, but it needs to be run an at least
python 3.6 as it was not tested using any previous versions.

I would also like to note that this is one of the first times that I have attempted to distribute python code,
so if there are any issues, please reach out to me and I will help to make sure everything is running properly.

I designed this app to be intuitive, so it has a basic html interface that can be used to complete all of the
tasks laid out in the coding challenge descriptions. On top of a nice interface to view the parsed data, you can also 
view the full API by going to http://127.0.0.1:5000/api/all. I would like to note now that I did not do this to the 
json spec exactly, as I am not super familar with it and did not want to keep you waiting. I am more than happy to update my program
and change it over to this spec if you want me to however!

I have included the virtual environmenet, in the folder venv, that I used to build this program. I included this as an optional download
so that it can be ensured that all of the proper modules are installed.