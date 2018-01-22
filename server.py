
#   CISC 435
#   Joshua Lee
#   13jl45
#   10112488

import socket
import threading
import thread
import time
import copy
from datetime import datetime
from random import randint
import urllib2

# variables to change execution dynamics of program
runTime = 15                    # allowed system runtime in seconds
runningClients = 3              # number of active clients (also # of sockets available)
waitingClients = 0              # number of waiting clients (in addition to active clients)
bonus = True                    # activate Bonus marks

# randomized server port
HOST = ''
PORT = randint(4000, 9999)

# access levels
platinumList = [0]          # *List = range of users for "*"
platinumAccess = 10         # *Access = allowed access/requests (limited to 10 on platinum for testing)
goldList = [2, 4, 6, 8]
goldAccess = 5
silverList = [1, 3, 7, 9]
silverAccess = 3

# random URLs and dummy responses
cache = {"http://www.google.com":"Google Stuff", "http://www.reddit.com":"Everything Forum", "http://www.facebook.com":"Social Network", "http://www.wimp.com":"Wholesome?", "http://www.hackerrank.com":"Coding Questions", "http://www.bing.com":"another search", "http://clientsusage.com": "You are not a Platinum user."}
# holds history of user data
history = {}

# Server thread
class Server(threading.Thread):
    def run(self):

        self.sock = socket.socket()         # creat
        self.sock.bind((HOST, PORT))        # bind socket (to local host)
        self.sock.listen(runningClients)                     # become a server socket + listen

        # create client handlers for number of "runningClients"
        for i in range(runningClients):
            thread.start_new_thread(clientHandler, (self.sock, i, runningClients))

# client handlers for server
def clientHandler(serverSock, x, y):

    while True:
        (clientSock, addr) = serverSock.accept()    # accept incoming socket connection requests
        clientData = clientSock.recv(1024)          # receive wanted URL
        if not clientData:                          # if nothing received, accept another client
            break
        print "Serving: ", clientData               # client name and access code


        clientInfo = [x.strip() for x in clientData.split(',')] # split name and access code

        # determine user category + privileges
        if int(clientInfo[1][-1]) in platinumList:
            access = platinumAccess
        elif int(clientInfo[1][-1]) in goldList:
            access = goldAccess
        else:
            access = silverAccess

        # send request limit for user
        print clientInfo[0], "Request limit:", access
        clientSock.send(str(access))

        # if bonus = True: real content    else: dummy content
        if bonus == True:
            runBonus(clientSock, access, clientInfo)
        else:
            runDummy(clientSock, access, clientInfo)

# run with real URLs and content
def runBonus(clientSock, access, clientInfo):
    temp = []           # user history
    requests = 0        # count number of requests
    url = ""            # requested url
    finished = False    # user finished requesting

    # while finish tag "<!-- 13jl45-DONE -->" not received and requests < limit
    while url != "<!-- 13jl45-DONE -->" and requests < access:

        url = clientSock.recv(1024)         # receive url

        # if url is finish tag, go to next client
        if url == "<!-- 13jl45-DONE -->":
            finished = True
            break

        # requesting special url: "http://clientsusage.com"
        elif url == "http://clientsusage.com":

            if access == platinumAccess:                # if platinum user
                clientSock.send("sending history")      # confirm with user
                snapshot = copy.deepcopy(history)       # copy current history
                for key, value in snapshot.iteritems(): # iterate through users and their history

                    clientSock.send("USER:" + str(key) + '\n')      # send user info
                    for site in value:                              # send each site visited
                        clientSock.send("    " + str(site) + '\n')
                clientSock.send("<!-- 13jl45-DONE -->")             # indicate end of sending
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " GRANTED: " + url)              # append to user history

            # if not platinum user, send back denied message
            else:
                clientSock.send(cache[url])
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " DENIED: " + url)

        # requesting regular url
        else:
            if "http://" in url:                    # if proper notation url
                clientSock.send("sending content")  # send content

                # if invalid url, return error and wait for another url
                try:
                    response = openURL(url)
                except urllib2.URLError:
                    clientSock.send("invalid URL")
                    continue

                # if valid url, read and send in 1024 byte sized packets
                html = response.read(1024)
                clientSock.send(html)
                while html != "":
                    html = response.read(1024)
                    clientSock.send(html)
                clientSock.send("<!-- 13jl45-DONE -->")     # indicate end of sending
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " GRANTED: " + url)      # apppend to user history
            else:
                clientSock.send("invalid URL")
                continue
        requests = requests + 1     # count requests

    # if user continues to request beyond limit, deny access until finished
    if finished == False:
        while url != "<!-- 13jl45-DONE -->":
            url = clientSock.recv(1024)
            if url == "<!-- 13jl45-DONE -->":
                break
            else:
                clientSock.send("Request limit reached.")
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " DENIED: " + url)
                break
    # append user history to entire user-base usage dictionary
    history[clientInfo[0]] = temp
#---------------------------------------------------------------------------
# dummy content execution (roughly same as "runBonus"
def runDummy(clientSock, access, clientInfo):
    temp = []
    requests = 0
    url = ""
    finished = False
    while url != "<!-- 13jl45-DONE -->" and requests < access:
        url = clientSock.recv(1024)
        if url == "<!-- 13jl45-DONE -->":
            finished = True
            break
        elif url == "http://clientsusage.com":
            if access == platinumAccess:
                clientSock.send("sending history")
                snapshot = copy.deepcopy(history)
                for key, value in snapshot.iteritems():

                    clientSock.send("USER:" + str(key) + '\n')
                    for site in value:
                        clientSock.send("    " + str(site) + '\n')
                clientSock.send("<!-- 13jl45-DONE -->")
            else:
                clientSock.send(cache[url])
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " DENIED: " + url)

        else:
            if url in cache:
                clientSock.send(cache[url])
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " GRANTED: " + url)
        requests = requests + 1
    if finished == False:
        while url != "<!-- 13jl45-DONE -->":
            url = clientSock.recv(1024)
            if url == "<!-- 13jl45-DONE -->":
                break
            else:
                clientSock.send("Request limit reached.")
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp.append(date + " DENIED: " + url)
    history[clientInfo[0]] = temp

#-------------------------------------------------------------------------
# check for 429 HTTP error and retry until accepted
def openURL(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError:
        time.sleep((randint(15, 20))/10.0)  # wait 1.5 to 2 seconds for request number to lower
        return urllib2.urlopen(url)
