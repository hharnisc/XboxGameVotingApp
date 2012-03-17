import os
import json
import logging
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template


class Game(db.Model):
    """
    Model for a game
    """
    title = db.StringProperty(required=True)
    owned = db.BooleanProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    votes = db.ListProperty(db.Key)

class Vote(db.Model):
    """
    Model for a vote
    """
    created = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):
    """
    Display owned games and games needed
    """
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'home.html')
        self.response.out.write(template.render(path,template_values))

class AddNew(webapp.RequestHandler):
    """
    Add a new game to the list
    """
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'addnew.html')
        self.response.out.write(template.render(path,template_values))

    def post(self):
        gamename=self.request.get('gamename')
        validGame = True

        #TODO: Clean up text input for query

        #handle no input case
        if not gamename:
            template_values = {'info_message':'Please Enter Game Name'}
            validGame = False
        results = Game.all().filter("title",gamename).fetch(1)

        #if game exists display error message
        if len(results):
            template_values = {'info_message':'Game Already Exists: ' + str(gamename)}
            validGame = False

        #add game to database
        if validGame:
            logging.info('Adding Game Name: ' + str(gamename))
            game = Game(title=gamename,owned=True)
            vote = Vote()
            vote.put()
            game.votes.append(vote.key())
            game.put()
            template_values = {'info_message':'Successfully Added ' + str(gamename)}

        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'addnew.html')
        self.response.out.write(template.render(path,template_values))

class GetGameData(webapp.RequestHandler):
    """
    Retrieve all game data from database and transmit JSON encoded data
    """
    def get(self):
        #TODO: Use paging method to grab all items

        #get all games that are not owned sorted by number of votes
        results = Game.all().filter("owned",False).fetch(1000)
        needDict = {}
        for result in sorted(results,lambda a,b:cmp(len(b.votes),len(a.votes))):
            needDict[result.title] = len(result.votes)

        #get all games that are owned sorted alphabetically
        results = Game.all().filter("owned",True).order("title").fetch(1000)
        ownedList = []
        for result in results:
            ownedList.append(result.title)

        self.response.out.write(json.dumps({"owned":ownedList,"need":needDict}))

app = webapp.WSGIApplication([('/', MainHandler),
                                ('/addnew',AddNew),
                                ('/getgamedata',GetGameData)],
                             debug=True)

