#!/usr/bin/env python
# server init checkup
# run a PodSixNet custom server on a specific port
# then run the client to communicate with the server through that port.

import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
from constants import *

#from constants import *
# from dot import Dot

# Each time a client connects,
# a new Channel based class will be created,
# subclass Channel
# to make server-representation-of-a-client class


class ClientChannel(PodSixNet.Channel.Channel):
    # calling connection.Send(mydata)

    def Network(self, data):
        print data

    def Network_place(self, data):
        # deconsolidate all of the data from the dictionary
        # reads the send data     
        x = data["x"]
        y = data["y"]
     
        # player number (1 or 0)
        num = data["num"]
        self.gameid = data["gameid"]
     
        # tell server to move ball coordinates
        self._server.moveBall(x, y, data, self.gameid, num)

    def Close(self):
        self._server.close(self.gameid)


class DotsServer(PodSixNet.Server.Server):
    # see take in various arguments
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        # call the PodSixNet class initializer n pass arguments 
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)

        self.games = []
        self.queue = None

        # keep track of the existing games, incrementing one for every game
        # created
        self.currentIndex = data["gameid"]

    def Connected(self, channel, addr):
        print 'new connection:', channel

        self.currentIndex += 1
        channel.gameid = self.currentIndex
        data['gameid'] = self.currentIndex

        if self.queue == None:
            # creates a new game and puts it in the queue
            # so that the next time a client connects, they are assigned to that game
            self.queue = Game(channel, self.currentIndex)

        else:
            channel.gameid = self.currentIndex
            self.queue.player1 = channel

            # sends a start game message to both players
            self.queue.player0.Send({"action": "startgame", "player": 0, "gameid": self.queue.gameid})
            self.queue.player1.Send({"action": "startgame", "player": 1, "gameid": self.queue.gameid})
            
            self.games.append(self.queue)
            # clear queue
            self.queue = None

    def moveBall(self, x, y, data, gameid, num):
        #finds the one with the same gameid as the client
        game = [i for i in self.games if i.gameid == gameid]

        #client
        if len(game) == 1:
            game[0].moveBall(x, y, data, num)

    def close(self, gameid):
        try:
            game = [a for a in self.games if a.gameid==gameid][0]
            game.player0.Send({"action":"close"})
            game.player1.Send({"action":"close"})
        except:
            pass

# keep track of state of the game, update to each client
class Game:

    def __init__(self, player0, currentIndex):
        # init coordinates
        self.x_0 = None
        self.y_0 = None

        # draw
        # TODO creates new game when first client connects
        # initialize the players
        self.player0 = player0
        self.player1 = None

        # gameid of game
        self.gameid = currentIndex

    def moveBall(self, x, y, data, num):
        # updates the ball coordinates
        self.x_0 = x
        self.y_0 = y

        data['x'] = self.x_0
        data['y'] = self.y_0
        data["action"] = "place"

        self.player0.Send(data)
        self.player1.Send(data)

print "<<<<<<<<<<<<<<<STARTING SERVER>>>>>>>>>>>>>>>>>"

# dotsServe = DotsServer()

# try:
address = raw_input("Host:Port (localhost:8000): ")

if not address:
    host, port = "localhost", 8000
else:
    host, port = address.split(":")

#init dots server
dotsServe = DotsServer(localaddr = (host, int(port)))

while True:
    # called once per game loop
    dotsServe.Pump()

    sleep(0.01)

