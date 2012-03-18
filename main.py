import os
import json
import Cookie
import logging
import datetime
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
        #simply render the page with now template values
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'home.html')
        self.response.out.write(template.render(path,template_values))

class AddNew(webapp.RequestHandler):
    """
    Add a new game to the list
    """
    def get(self):
        #simply render the page with now template values
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'addnew.html')
        self.response.out.write(template.render(path,template_values))

    def post(self):
        #attempt to grab a cookie from the user
        voted = self.request.cookies.get('voted', '')

        #if user's cookie is still active then don't let them vote
        if voted:
            #send error message to user
            template_values = {'info_message':'Maximum Daily Votes Reached'}
        else:
            validGame = True
            #get the game title from the request
            gamename=self.request.get('gamename')

            #handle no input case
            if not gamename:
                template_values = {'info_message':'Please Enter Game Name'}
                validGame = False

            #attempt to locate the game in the database
            results = Game.all().filter("title",gamename).fetch(1)

            #if game exists display error message
            if len(results):
                template_values = {'info_message':'Game Already Exists: ' + str(gamename)}
                validGame = False

            #add game to database if valid game
            if validGame:
                logging.info('Adding Game Name: ' + str(gamename))
                #create a game
                game = Game(title=gamename,owned=False)
                #create a vote
                vote = Vote()
                vote.put()
                #add the vote to the game's votes
                game.votes.append(vote.key())
                game.put()
                #construct message to send to user
                template_values = {'info_message':'Successfully Added ' + str(gamename)}
                #create a cookie that expires at 23:59:59
                C = Cookie.SimpleCookie()
                C["voted"] = "voted"
                theTime = datetime.datetime.now()
                #set expiration for tonight at 23:59:59
                expireTime = datetime.datetime(theTime.year,theTime.month,theTime.day,23,59,59)
                C['voted']['expires'] = expireTime.strftime('%a, %d %b %Y %H:%M:%S') # Wdy, DD-Mon-YY HH:MM:SS
                header_value = C.output(header='')
                self.response.headers.add_header("Set-Cookie", header_value)

        path = os.path.join(os.path.dirname(__file__), 'templates'+os.sep+'addnew.html')
        self.response.out.write(template.render(path,template_values))

class GetGameData(webapp.RequestHandler):
    """
    Retrieve all game data from database and transmit JSON encoded data
    """
    def get(self):
        #TODO: Use paging method to grab all items -- 1000 is a possible limit

        #get all games that are not owned, sorted by number of votes --cutoff at 50 characters
        results = Game.all().filter("owned",False).fetch(1000)
        needList = []
        for result in sorted(results,lambda a,b:cmp(len(b.votes),len(a.votes))):
            needList.append({"game":result.title,"votes":len(result.votes)})

        #get all games that are owned, sorted alphabetically -- cutoff at 50 characters
        results = Game.all().filter("owned",True).order("title").fetch(1000)
        ownedList = []
        for result in sorted(results,lambda a,b:cmp(a.title.lower(),b.title.lower())):
            ownedList.append(result.title)

        #transmit jason data to user
        self.response.out.write(json.dumps({"owned":ownedList,"need":needList}))

class VoteGame(webapp.RequestHandler):
    """
    Vote for a game
    """
    def post(self):
        voted = self.request.cookies.get('voted', '')
        #if user's cookie is still active then don't let them vote
        if voted:
            success = False
            message = "Maximum Daily Votes Reached"
        else:
            #check databse for game title
            gamename=self.request.get('gamename')
            result = Game.all().filter("title",gamename).fetch(1)[0]
            #if title exists then add a vote to the game
            if result:
                #create a new vote
                vote = Vote().put()
                #add the vote to the result
                result.votes.append(vote)
                result.put()
                C = Cookie.SimpleCookie()
                C["voted"] = "voted"
                #get the current time in central time zone
                theTime = datetime.datetime.now()
                #set expiration for tonight at 23:59:59
                expireTime = datetime.datetime(theTime.year,theTime.month,theTime.day,23,59,59)
                C['voted']['expires'] = expireTime.strftime('%a, %d %b %Y %H:%M:%S') # Wdy, DD-Mon-YY HH:MM:SS
                header_value = C.output(header='')
                self.response.headers.add_header("Set-Cookie", header_value)
                success = True
                message = "Vote has been received!"
            else:
                success = False
                message = "Vote has failed."
        #transmit jason data to user
        self.response.out.write(json.dumps({"success":success,"message":message}))

class SetGameOwned(webapp.RequestHandler):
    """
    Set a game as owned
    """
    def post(self):
        #check databse for game title
        gamename=self.request.get('gamename')
        result = Game.all().filter("title",gamename).fetch(1)[0]
        #if game exists set game to owned
        if result:
            result.owned = True
            result.put()
            success = True
            message = "Game is now owned!"
        else:
            success = False
            message = "Setting game to owned has failed."
        #transmit jason data to user
        self.response.out.write(json.dumps({"success":success,"message":message}))

#routing scheme
app = webapp.WSGIApplication([('/', MainHandler),
                                ('/addnew',AddNew),
                                ('/getgamedata',GetGameData),
                                ('/votegame',VoteGame),
                                ('/setgameowned',SetGameOwned)],
                             debug=True)

