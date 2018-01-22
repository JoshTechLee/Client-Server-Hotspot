
#   CISC 435
#   Joshua Lee
#   13jl45
#   10112488

# Environment to start both client + server with ease
# Attributes may be set within server.py

from server import Server
from client import Client

def main():
    server = Server()
    client = Client()

    print ("Server started")
    server.start()
    print ("Client started")
    client.start()

main()


