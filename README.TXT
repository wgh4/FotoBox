***************************
* README.TXT
***************************
CIT FotoBox Application
Name: fotobox.py
Version: 1.RELEASE
Author: Robert Knaap
StudentId: R00091539
email: robert.knaap@emc.com
phone: 086-6050603
Date: Tue Dec 4, 2012
SourceCode: https://github.com/wgh4/FotoBox
GAE URL: citfotobox.appspot.com
***************************
* CIT FotoBox Application
***************************

The CIT FotoBox application is a photo sharing website that is based on the GAE image sharing example that can
be found in the GAE documentation http://code.google.com/p/google-app-engine-samples/source/browse/trunk/image_sharing
and some of the image transformation developers code from https://developers.google.com/appengine/docs/python/images/usingimages
The application incorporates Stylesheets, User feedback, User Authentication and Emial functionality.

The application will be called CIT Fotobox (foto is dutch for photo as I am from holland :)

***************************
* How does it work
***************************
Users with a valid google user account can login to the application and are shown the welcome page. From the welcome page that can enter the main foto catalog
From the main page the user has the option to view the contents of an existing fotobox, do a search on the fotos, submit feedback or create a new fotobox container.
Selecting a fotobox will display the contents of the box and will show a thumbnail of all fotos containing within the box. Selecting a thumbnail will display the full
foto. The user has the option to email the foto to him or herself and to other users or download the image (select download and then right mouse click, save as). New fotos (JPEG, GIF, PNG files) can be uploaded by selecting the upload new foto option
When uploading a new foto, the user has to provide a name, caption and some TAGS. The TAGS can then be used for searching.

***************************
* Architecture
***************************
The application uses the following Google App Engine modules

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

###########################################
# Classes
###########################################

Email Handler - shows email form and sends email
    
FotoBoxFeedback displays Feedback form

FotoBoxFeedbackPoster submits feedback

FotoBoxIndex shows list of fotoboxes on index form

FotoBoxCreate - FotoBox Handler for creating a new fotobox via HTML formand Renders: new.html

FotoBoxView for viewing the foto's in a particular footboy
    Args: fotobox_key: the datastore key for the fotobox to view.
    Renders: fotobox.html, max 5 fotos per Row

FotoBoxUploadFoto-  FotoBox Handler for uploading fotos in a particular fotobox
    Args: fotobox_key: the datastore key for the fotobox to view, fotobox_name: the name of the fotobox
    Renders: fotobox.html

FotoBoxShowFoto-  FotoBox Handler for viewing a single foto.
     Args: foto_key: the datastore key for the foto to view.
     Renders: show_foto.html
     This Handler does not serve the foto, but only renders the page containing it. The foto is served in FotoBoxServeFoto.

FotoBoxServeFoto-  FotoBox Handler for dynamically serving a foto from the datastore.
     Args: foto_key: the datastore key for the foto to view, display_type: the type of image to serve (image or thumbnail)
 
     This Handler pulls the appropriate data out of the datastore and serves it.

FotoBoxSearch -  FotoBox Handler for searching fotos by tag. Displays the tag search box and possibly a list of results.

FotoBoxLoginHandler-  FotoBox Authentication Handler 

***************************
* Templates
***************************
All templates inherit from the master.html template and use the stylesheet.css

***************************
* FORMS
***************************

Welcome FORM - Welcome Page, does authentication check and shows logon / logoff option
Index FORM - Displays all existing fotoboxes. provides links to create new fotobox, search and feedback
Feedback FORM - Displays feedback form and all existing feedback records. provides links to index page and search
Search FORM - Displays search form and lets user search on all tags. provides links to index page and feedback page

Fotobox FORM - Displays  fotobox page with thumbnail of all fotos. provides links to index page, feedback page and add new 
New FORM - Displays new fotobox page and lets user submit new fotobox collection. provides links to index page and feedback page

Upload FORM - Enables the users to add a new foto to a fotobox. provides links to index page and feedback page
Show_foto FORM - Shows the full view of a foto. provides links to index page and feedback page and link back to the fotobox container
Email FORM - Enables the user to email a foto to himself and additional users. provides links to index page and feedback page
EmailSend FORM - confirmation page

Master FORM

***************************
* Data Model
***************************

All Foto Containers will be defined by the clsFotoBox class:

class clsFotoBox(db.Model):
  name = db.StringProperty()  # name: Name for the fotobox collection
  description = db.StringProperty(multiline=True) # description: Description of the fotobox collection
  owner = db.UserProperty() # owner: Google Account of the person who owns the album
  creation_date = db.DateTimeProperty(auto_now_add=True) # Creation_date: DateTime the album was created

All Foto's will be defined by the clsFoto class:  

class clsFoto(db.Model):
  name = db.StringProperty() #user entered name for the foto
  caption = db.StringProperty(multiline=True) #user entered caption for the foto
  submitter = db.UserProperty() #Google Account of the person who submitted the picture
  submission_date = db.DateTimeProperty(auto_now_add=True) #DateTime the picture was submitted
  fotobox = db.ReferenceProperty(clsFotoBox, collection_name='pictures') #reference to fotobox the picture is in
  tags = db.StringListProperty() # a list of tags assigned to the foto
  data = db.BlobProperty() # data for the original picture, converted into png format
  thumbnail_data = db.BlobProperty() #png format data for the thumbnail for this picture
  
The application uses 2 BlobProperty fields to store the images and the thumbnails (> 1Mb)  
  
All Feedback will be defined by the clsFeedbackMessage class: 

class clsFeedbackMessage(db.Model):
    user = db.StringProperty(required=True) #Google Account of the person who submitted the picture
    timestamp = db.DateTimeProperty(auto_now_add=True) #DateTime the feedback was submitted
    message = db.TextProperty(required=True) #user defined feedback

***************************
* User Authentication
***************************

Only users with a valid google user account can use the application.
The login: required option in app.yaml will force this

***************************
* GAE url
***************************

The application is running in GAE and can be accessed on the following URL: http://citfotobox.appspot.com/
4 fotoboxes are created with different photos and some users left some Feedback
Please make sure the files to be uploaded are less than 1 Mb in size.


