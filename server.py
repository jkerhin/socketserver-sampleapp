"""Simple app to record messages from multiple TCP/IP clients, storing the message and
message metadata in a central location.

Note that sockets and threads on Windows behave quite differently than they do on unix-y
systems. The `socket.accept()` and `socket.recv()` calls are _totally_ blocking on
Windows - while blocked for one of these calls, not even KeyboardInterrupt will be
handled.

The solution is to make sure that all Windows sockets - both the bound server socket as
well as the "spawned" connection sockets - have a timeout set. Once the timeout is
reached, the Ctrl+C signal can be caught and handled properly by the app
"""
import contextlib
import logging
import socket
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass
class Message:
    receipt_time: datetime
    client: Tuple[str, int]
    data: bytes


class ServerApp:
    def __init__(self, host: str = "localhost", port: int = 8675) -> None:
        self._messages: list = []
        self._thread_pool: list = []

        self.shut_down = threading.Event()
        self.shut_down.clear()

        self.lock = threading.Lock()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))

    def shutdown(self):
        logging.info("Shutting down ServerApp, joining threads")
        for thread in self._thread_pool:
            thread.join(0.1)
        logging.info(
            "Logged %d messages:\n\t%s", len(self._messages), str(self._messages)
        )

    def message_appender(self, conn: socket.socket, addr: Tuple[str, int]):
        cur_thread = threading.current_thread()
        thread_name = cur_thread.name
        conn.settimeout(1)
        logging.info(f"Starting thread {thread_name}")
        while not self.shut_down.is_set():
            with contextlib.suppress(socket.timeout):
                if data := conn.recv(1024):  # .recv() blocks KeyboardInterrupt too...
                    logging.info(data)  # NB `data` is bytes, not str
                    recv_time = datetime.now()
                    with self.lock:
                        self._messages.append(Message(recv_time, addr, data))

    def run(self):
        logging.info("Starting ServerApp.run")
        # Set timeout to allow KeyboardInterrupt to be caught
        self.server_socket.settimeout(1)
        self.server_socket.listen(20)
        while not self.shut_down.is_set():
            with contextlib.suppress(socket.timeout):
                logging.debug("Waiting for client")
                conn, addr = self.server_socket.accept()  # Absolute blocking call
                logging.info(f"Accepted client {addr}")
                t = threading.Thread(target=self.message_appender, args=(conn, addr))
                logging.debug("Starting thread")
                t.start()
                logging.debug("Adding to thread pool")
                self._thread_pool.append(t)


def main():
    app = ServerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        logging.info("Caught Ctrl+C, begin shut down")
    finally:
        app.shut_down.set()
        app.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
