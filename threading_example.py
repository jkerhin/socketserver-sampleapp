"""Source:
https://docs.python.org/3/library/socketserver.html?highlight=socketserver#asynchronous-mixins

Again, this still didn't meet the need as each handler can handle only one message.
"""
import socket
import socketserver
import threading


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), "ascii")
        cur_thread = threading.current_thread()
        response = bytes(f"{cur_thread.name}: {data}", "ascii")
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, "ascii"))
        response = str(sock.recv(1024), "ascii")
        print(f"Received: {response}")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8675

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(ip, port, "Hello World 1")
        client(ip, port, "Hello World 2")
        client(ip, port, "Hello World 3")

        server.shutdown()
