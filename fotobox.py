#!/usr/bin/python2.7
#
# Concept is based on the GAE sample code snippits that can be found in the GAE documentation
# (http://code.google.com/p/google-app-engine-samples/source/browse/trunk/image_sharing)
#
# CIT FotoBox is a simple photo sharing application running on Googles App Engine.
###########################################

###########################################
# Parameters
###########################################
SENDER = 'robert.knaap@gmail.com'

###########################################
# Import GAE libraries
###########################################
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

###########################################
# Import python functions
###########################################
import cgi    # to escape special characters from html
import os     # import os pathing functions
import re     # regular expression functions

###########################################
# Define FotoBox Class
###########################################
class clsFotoBox(db.Model):
  name = db.StringProperty()  # name: Name for the fotobox collection
  description = db.StringProperty(multiline=True) # description: Description of the fotobox collection
  owner = db.UserProperty() # owner: Google Account of the person who owns the album
  creation_date = db.DateTimeProperty(auto_now_add=True) # Creation_date: DateTime the album was created
  
###########################################
# Define Foto Class
###########################################
class clsFoto(db.Model):
  name = db.StringProperty() #user entered name for the foto
  caption = db.StringProperty(multiline=True) #user entered caption for the foto
  submitter = db.UserProperty() #Google Account of the person who submitted the picture
  submission_date = db.DateTimeProperty(auto_now_add=True) #DateTime the picture was submitted
  fotobox = db.ReferenceProperty(clsFotoBox, collection_name='pictures') #reference to fotobox the picture is in
  tags = db.StringListProperty() # a list of tags assigned to the foto
  data = db.BlobProperty() # data for the original picture, converted into png format
  thumbnail_data = db.BlobProperty() #png format data for the thumbnail for this picture

###########################################
# Define FeedbackMessage Class
###########################################
class clsFeedbackMessage(db.Model):
    user = db.StringProperty(required=True) #Google Account of the person who submitted the picture
    timestamp = db.DateTimeProperty(auto_now_add=True) #DateTime the feedback was submitted
    message = db.TextProperty(required=True) #user defined feedback

###########################################
# Define Email Handler
# shows email form and sends email
###########################################
class EmailHandler(webapp.RequestHandler):
    #Displays the email form.
    def get(self, foto_key):
        oFoto = db.get(foto_key)
        oUser = users.get_current_user()
        colTemplate_params = {
        'user': oUser.email(),
        'foto_key': foto_key,
        'foto': oFoto
         }
        strPath = os.path.join(os.path.dirname(__file__), 'templates/email.html')
        oPage = template.render(strPath, colTemplate_params) 
        self.response.out.write(oPage)
    #Sends the email
    def post(self, foto_key):
        #Send email to logged in user
        oUser = users.get_current_user()
        strMailto = oUser.email()
        #Get cc'ed users from form
        strMailcc = self.request.get('mailcc')
        if mail.is_email_valid(strMailcc):
            strMailto = strMailto + ',' + strMailcc
        #Retrieve message text    
        strMailbody = cgi.escape(self.request.get('mailbody'), quote=True)        
        if strMailbody =='':
           strMailbody = 'Checkout the attached foto I found on fotobox!'    

        oMessage = mail.EmailMessage()
        oMessage.sender = SENDER     #only allowed to send as application admin/owner
        oMessage.to =strMailto
        oMessage.subject = cgi.escape(self.request.get('mailsubject'))
        oMessage.body = strMailbody
        
        #Get foto Object
        oFoto = db.get(foto_key)
        strFotoname = oFoto.name
        
        #strip all spaces from foto.name
        strFotoname = re.sub(r'\s+', '', strFotoname) + '.png'
        #attach foto
        oMessage.attachments=[(strFotoname, oFoto.data)]
        #send message
        try:
           oMessage.send()
        except mail.Error, e:
           self.error(400)
           self.response.out.write('Error: ' + str(e)) 
             
        colTemplate_params = {'mailto': strMailto,
                           'foto_key': foto_key,
                           'foto': oFoto
                          }
        strPath = os.path.join(os.path.dirname(__file__), 'templates/emailsend.html')
        oPage = template.render(strPath, colTemplate_params) 
        self.response.out.write(oPage)
    
###########################################
# Define Feedback Page
###########################################
class FotoBoxFeedback(webapp.RequestHandler):
  def get(self):
    colMessages = clsFeedbackMessage.all().order('-timestamp')
    colTemplate_params = {'msg_list': colMessages,}
    strPath = os.path.join(os.path.dirname(__file__), 'templates/feedback.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage)
    
###########################################
# Define Feedback Poster (talk)
###########################################
class FotoBoxFeedbackPoster(webapp.RequestHandler):
  def post(self):
    oUser = users.get_current_user()
    strMsgtext = cgi.escape(self.request.get("message"), quote=True)
    if strMsgtext :
       oMsg = clsFeedbackMessage(user=oUser.nickname(), message=strMsgtext)
       oMsg.put() 
       # After adding the feedback redirect to the feedback page,
       self.redirect('/feedback')
    else:
       self.error(400)
       self.response.out.write('Please provide Feedback Text. Select BACK button in browser to retry')

###########################################
# Define FotoBox List 
###########################################
class FotoBoxIndex(webapp.RequestHandler):
  #Handler to list fotoboxes
  def get(self):
    #Query all fotoboxes ordered by creation_date
    colFotoboxes = clsFotoBox.all().order('-creation_date')   
    colTemplate_params = {'fotoboxes': colFotoboxes,}
    strPath = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage)

###########################################
# FotoBox Handler for creating a new fotobox via HTML form
#    Renders: new.html
###########################################
class FotoBoxCreate(webapp.RequestHandler):
  def get(self):
    #Displays the fotobox creation form.
    strPath = os.path.join(os.path.dirname(__file__), 'templates/new.html')
    oPage = template.render(strPath, {}) 
    self.response.out.write(oPage)

  def post(self):
    #Processes a fotobox creation request
    strFotoboxname = cgi.escape(self.request.get('fotoboxname'), quote=True)
    if strFotoboxname:      
       strFotoboxdescription =  cgi.escape(self.request.get('fotoboxdescription'), quote=True)
       if strFotoboxdescription == '':
          strFotoboxdescription = strFotoboxname
       clsFotoBox(name=strFotoboxname,
                  description=strFotoboxdescription,
                  owner=users.get_current_user()).put()
       #redirect back to main catalog page
       self.redirect('/index')
    else:
       self.error(400)
       self.response.out.write('Fotobox Name is a mandatory field. Select BACK button in browser to retry')

###########################################
# FotoBox Handler for viewing the foto's in a particular fotobox
#    Args: fotobox_key: the datastore key for the fotobox to view.
#    Renders: fotobox.html, max 5 fotos per Row
###########################################
class FotoBoxView(webapp.RequestHandler):
  def get(self, fotobox_key):
    #get fotobox from key
    oFotobox = db.get(fotobox_key)
    colFotos = []
    iResults = 0
    
    #Loop through pictures in fotobox
    for oPicture in oFotobox.pictures:
      if iResults % 5 == 0:  # display 5 fotos on each row
        colDisplayRow = []
        colFotos.append(colDisplayRow)
      colDisplayRow.append(oPicture)
      iResults += 1

    # Display the fotobox form
    # pass in results, key, name and fotos collection
    
    colTemplate_params = {
        'num_results': iResults,
        'fotobox_key': oFotobox.key(),
        'fotos': colFotos,
        'fotobox_name': oFotobox.name        
      }
    strPath = os.path.join(os.path.dirname(__file__), 'templates/fotobox.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage)

###########################################
# FotoBox Handler for uploading fotos in a particular fotobox
#    Args: fotobox_key: the datastore key for the fotobox to view.
#          fotobox_name: the name of the fotobox
#    Renders: fotobox.html
###########################################
class FotoBoxUploadFoto(webapp.RequestHandler):

  def get(self, fotobox_key):
    #get fotobox from key
    oFotobox = db.get(fotobox_key)
    
    # Display the upload form and pass in fotobox_key and name
   
    colTemplate_params = {'fotobox_key': oFotobox.key(),'fotobox_name': oFotobox.name}
    strPath = os.path.join(os.path.dirname(__file__), 'templates/upload.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage) 
    
  def post(self, fotobox_key):
    #Process the foto upload request
    #pass in key to retrieve fotobox collection
    oFotobox = db.get(fotobox_key)
    if oFotobox is None:
      self.error(400)
      self.response.out.write('FotoBox cannot be found with supplied key')

    #use cgi.escape functions to escape special characters like "<>&."
    strName = cgi.escape(self.request.get('name'), quote=True)
    
    if strName:
      strCaption = cgi.escape(self.request.get('caption'), quote=True)

      #process tags and split them, add them to tags collection
      colTags = cgi.escape(self.request.get('tags'), quote=True).split(',')
      colTags = [oTag.strip() for oTag in colTags]
    
      # Get the actual image
      oFoto_data = self.request.POST.get('fotofile').file.read()
      
      if oFoto_data:
        try: 
          oFoto = images.Image(oFoto_data)
          
          #Adjusts the contrast and color levels of an image according
          #to an algorithm for improving photographs          
          oFoto.im_feeling_lucky()

          #transform image to PNG
          oPng_data = oFoto.execute_transforms(images.PNG)
          #resize the image
          oFoto.resize(100, 100)
          #generate thumbnail
          oThumbnail_data = oFoto.execute_transforms(images.PNG)
          #save foto
          clsFoto(submitter=users.get_current_user(),
                  name=strName,
                  caption=strCaption,
                  fotobox=oFotobox,
                  tags=colTags,
                  data=oPng_data,
                  thumbnail_data=oThumbnail_data).put()
          #redirect to fotobox page
          self.redirect('/fotobox/%s' % oFotobox.key())
        except: 
          self.error(400)
          self.response.out.write('Unable to process image. The image is either to large or not a JPEG, GIF or PNG format. Select BACK button in browser to retry')
      else:
        self.error(400)
        self.response.out.write('No foto was selected for upload. Select BACK button in browser to retry')
    else:
       self.error(400)
       self.response.out.write('Foto Name is a mandatory field. Select BACK button in browser to retry')

###########################################
# FotoBox Handler for viewing a single foto.
#    Args: foto_key: the datastore key for the foto to view.
#    Renders: show_foto.html
#    This Handler does not serve the foto, but only renders
#    the page containing it. The foto is served in FotoBoxServeFoto.
###########################################
class FotoBoxShowFoto(webapp.RequestHandler):
  def get(self, foto_key):
    #get foto and render html page
    oFoto = db.get(foto_key)

    # Display the show_foto form.
    # pass in foto object and foto_key

    colTemplate_params = {'foto': oFoto,
                       'foto_key': oFoto.key(),
                      }
    strPath = os.path.join(os.path.dirname(__file__), 'templates/show_foto.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage)
    

###########################################
# FotoBox Handler for dynamically serving a foto from the datastore.
#    Args: foto_key: the datastore key for the foto to view.
#          display_type: the type of image to serve (image or thumbnail)
#
#    This Handler pulls the appropriate data out of the datastore
#    and serves it.
###########################################
class FotoBoxServeFoto(webapp.RequestHandler):
  def get(self, display_type, foto_key):

    oFoto = db.get(foto_key)

    if display_type == 'image':
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(oFoto.data)
    elif display_type == 'thumbnail':
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(oFoto.thumbnail_data)
    else:
      self.error(500)
      self.response.out.write(
          'Unable to determine type of foto to serve.')

###########################################
# FotoBox Handler for searching fotos by tag.
# displays the tag search box and possibly a list of results.
###########################################
class FotoBoxSearch(webapp.RequestHandler):
  def get(self):
    query = self.request.get('q')
    colFotos = []
    if query:
      # The TAGS StringListProperty allows for searching for
      # the occurrence of the searchterm in any of the tags.
      colFotos = clsFoto.all().filter('tags =', query)
    else:
      query = ''
    # Display the search form.
    # pass in query object and fotos collection

    colTemplate_params = {
        'query': query,
        'fotos': colFotos,
      }
    strPath = os.path.join(os.path.dirname(__file__), 'templates/search.html')
    oPage = template.render(strPath, colTemplate_params) 
    self.response.out.write(oPage)           

###########################################
# FotoBox Authentication Handler 
###########################################   
class FotoBoxLoginHandler(webapp.RequestHandler):
    def get(self):
        oUser = users.get_current_user()
        if oUser is None:
           strUrl = users.create_login_url("/")
           colTemplate_params = {'authenticated': False, 'url': strUrl}
        else:
           strUrl = users.create_logout_url("/")
           colTemplate_params = {'authenticated': True, 'username': oUser.nickname(), 'url': strUrl}

        strPath = os.path.join(os.path.dirname(__file__), 'templates/welcome.html')
        oPage = template.render(strPath, colTemplate_params) 
        self.response.out.write(oPage)           

###########################################
# FotoBox Application definition and URLmapper 
###########################################     
application = webapp.WSGIApplication([('/', FotoBoxLoginHandler),
                                       ('/index', FotoBoxIndex),
                                       ('/new', FotoBoxCreate),
                                       ('/fotobox/([-\w]+)', FotoBoxView),
                                       ('/upload/([-\w]+)', FotoBoxUploadFoto),
                                       ('/feedback', FotoBoxFeedback),
                                       ('/sendmail/([-\w]+)', EmailHandler),
                                       ('/show_image/([-\w]+)', FotoBoxShowFoto),
                                       ('/(thumbnail|image)/([-\w]+)', FotoBoxServeFoto),
                                       ('/talk', FotoBoxFeedbackPoster),
                                       ('/search', FotoBoxSearch)],
                                       debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
