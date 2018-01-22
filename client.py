import socket
import threading
import thread
import time
from random import randint
import server
import os

# retrieve number of clients from server.py
runningClients = server.runningClients + server.waitingClients

# retrieve address of server
HOST = server.HOST
PORT = server.PORT

# list of sites to choose from
sites = ["http://python.com", "http://www.google.com", "http://www.reddit.com", "http://www.facebook.com", "http://www.wimp.com", "http://www.hackerrank.com", "http://www.bing.com", "http://clientsusage.com", "http://clientsusage.com"]

# start client thread
class Client(threading.Thread):
    def run(self):

        # create number of client generators based on runningClient
        for i in range(runningClients):
            thread.start_new_thread(clientGenerator, (i, runningClients))

        # stop program after set time
        time.sleep(server.runTime)


# client generator
def clientGenerator(num, increments):

    clientNum = num                         # initial client number
    virtualThread = "clientGenerator", num    # client generator number
    print virtualThread

    # simulate a queue of clients
    while True:
        clientName = "client" + str(clientNum)      # generate client name
        id = '{:03}'.format(randint(50, 300))       # assign access code
        print "    " + clientName + ": Access", id

        # create socket and connect
        sock = socket.socket()
        sock = connect(sock, HOST, PORT)    # call "connect" to continuously attempt to connect

        sock.send("client" + str(clientNum) + ", " + str(id))   # send client ID
        reply = sock.recv(1024)     # receive request number

        # if bonus from server set to true:
        if server.bonus == True:
            requests = randint(1, int(reply) + 2)   # randomize amount of requests
            print "    " + clientName + " REQUESTING:", requests

            # generate requests
            for i in range(requests):
                site = sites[randint(0, len(sites) - 1)]    # choose random URL
                print "    " + clientName + ":", site
                sock.send(site)                             # send to server
                print "    " + clientName + ": waiting"
                reply = sock.recv(1024)                     # receive status of request

                # if platinum user and request special URL:
                if reply == "sending history":
                    folder = os.path.dirname(__file__)
                    filename = os.path.join(folder, 'History', clientName + ".txt")
                    filename = open(filename, "w+")     # write to <client_name>.txt
                    while reply != "<!-- 13jl45-DONE -->":  # retrieve until end tag
                        reply = sock.recv(1024)             # receive replies
                        if "<!-- 13jl45-DONE -->" in reply:
                            break
                        filename.write(reply)                      # write to file
                    filename.close()

                # if requesting other URLs
                elif reply == "sending content":
                    chunks = []     # holds pieces of received data
                    while reply != "<!-- 13jl45-DONE -->":  # retrieve data until end tag
                        reply = sock.recv(1024)
                        if ("<!-- 13jl45-DONE -->" in reply) or ("invalid URL" in reply):
                            break
                        chunks.append(reply)  # append replies into list
                    if reply == "invalid URL":
                        print "    " + clientName + " ERROR:", "\"" + reply + "\""
                        continue
                    html = ''.join(chunks)      # write entire data set into html
                    print "    " + clientName + " RECEIVED:", html[0:10], "...", html[30:40], "...", html[-10:]    # print first and last 10 characters of file

                # if access denied for some reason, print the error and continue
                else:
                    print "    " + clientName + " ERROR:", "\"" + reply + "\""
                    if reply == "Request limit reached.":
                        break

            # indicate end of user requests
            sock.send("<!-- 13jl45-DONE -->")
#------------------------------------------------------------------------------
        # if bonus not selected, do this
        else:
            requests = randint(1, int(reply) + 1)
            print clientName, " REQUESTING:", requests
            for i in range(requests):
                site = sites[randint(0, len(sites) - 1)]
                print site
                sock.send(site)
                print "    " + clientName + ": waiting"
                reply = sock.recv(1024)
                if reply == "sending history":
                    f = open(clientName + ".txt", "w+")
                    while reply != "<!-- 13jl45-DONE -->":
                        reply = sock.recv(1024)
                        if "<!-- 13jl45-DONE -->" in reply:
                            break
                        f.write(reply)
                    f.close()
                else:
                    print "    " + clientName + ": \"" + reply + "\""
            sock.send("<!-- 13jl45-DONE -->")
#----------------------------------------------------------------------------------
        # close client socket
        sock.close()
        # wait 0.2 to 0.4 seconds before creating new client
        time.sleep((randint(20, 40) / 100.0))
        # generate number
        clientNum = clientNum + increments

# continuosly attempt to connect to server
def connect(sock, host, port):
    try:
        sock.connect((host, port))
    except socket.error as msg:
        print msg
        time.sleep(1)
        connect(sock, host, port)   # recursive call until connected
    return sock