"""Largely based off the socketserver std library example:

https://docs.python.org/3/library/socketserver.html?highlight=socketserver#socketserver-tcpserver-example

Note that this does not meet our needs as each `MyTCPHandler` processes exactly one
messages' worth of data and then terminates. Additionally, only one connection can be
open at a time.
"""
import socketserver
import sys


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def setup(self) -> None:
        print("I'm setting up, baby!")

    def finish(self) -> None:
        print("Shutting down!")

    def handle(self) -> None:
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} wrote:")
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    try:
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
    except KeyboardInterrupt:
        print("Recieved Ctrl+C, shutting down...")
    finally:
        sys.exit(0)
