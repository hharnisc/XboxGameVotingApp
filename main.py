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
        #self.request.remote_addr()
        #voted = self.request.cookies.get('voted', '')

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
            game = Game(title=gamename,owned=False)
            vote = Vote()
            vote.put()
            game.votes.append(vote.key())
            game.put()
            template_values = {'info_message':'Successfully Added ' + str(gamename)}

        #TODO: add cookie to header

        #self.response.headers.add_header(
        #    'Set-Cookie',
        #    'username=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT'\
        #    % username.encode())

        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'addnew.html')
        self.response.out.write(template.render(path,template_values))

class GetGameData(webapp.RequestHandler):
    """
    Retrieve all game data from database and transmit JSON encoded data
    """
    def get(self):
        #TODO: Use paging method to grab all items

        #get all games that are not owned sorted by number of votes --cutoff at 50 characters
        results = Game.all().filter("owned",False).fetch(1000)
        needList = []
        for result in sorted(results,lambda a,b:cmp(len(b.votes),len(a.votes))):
            needList.append({"game":result.title[:50],"votes":len(result.votes)})

        #get all games that are owned sorted alphabetically -- cutoff at 50 characters
        results = Game.all().filter("owned",True).order("title").fetch(1000)
        ownedList = []
        for result in results:
            ownedList.append(result.title[:50])

        self.response.out.write(json.dumps({"owned":ownedList,"need":needList}))

class VoteGame(webapp.RequestHandler):
    """
    Vote for a game
    """
    #voted = self.request.cookies.get('voted', ''
    def get(self):
        gamename=self.request.get('gamename')
        result = Game.all().filter("title",gamename).fetch(1)[0]
        #logging.info(result[0].votes)
        vote = Vote().put()
        result.votes.append(vote)
        result.put()


class SetGameOwned(webapp.RequestHandler):
    """
    Set a game as owned
    """

app = webapp.WSGIApplication([('/', MainHandler),
                                ('/addnew',AddNew),
                                ('/getgamedata',GetGameData),
                                ('/votegame',VoteGame)],
                             debug=True)

