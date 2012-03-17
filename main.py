from google.appengine.ext import webapp
from google.appengine.ext import db

class Game(db.Model):
    """
    Model for a game
    """
    id = db.IntegerProperty
    title = db.StringProperty
    owned = db.BooleanProperty
    created = db.DateTimeProperty(auto_now_add=True)

class Vote(db.Model):
    """
    Model for a vote
    """
    gameId = db.IntegerProperty
    created = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):
    """
    Display owned games and games needed
    """
    def get(self):
        self.response.out.write('Hello world!')

class AddNew(webapp.RequestHandler):
    """
    Add a new game to the list
    """
    def get(self):
        self.response.out.write('Add New')

    def post(self):
        pass

class GetGameData(webapp.RequestHandler):
    """
    Retrieve all game data from database and transmit JSON encoded data
    """
    pass

app = webapp.WSGIApplication([('/', MainHandler),
                                ('/addnew',AddNew),
                                ('/getgamedata',GetGameData)],
                             debug=True)

