from google.appengine.ext import webapp
from google.appengine.ext import db

class Game(db.Model):
    id = db.IntegerProperty
    title = db.StringProperty
    owned = db.BooleanProperty
    created = db.DateTimeProperty(auto_now_add=True)

class Vote(db.Model):
    gameId = db.IntegerProperty
    created = db.DateTimeProperty(auto_now_add=True)
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


app = webapp.WSGIApplication([('/', MainHandler)],
                             debug=True)

