#!/usr/bin/env python3

import socket, select, sys, os, sqlite3, signal

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
from game import Game
# import game, zombie, player

class Server:
    
    def __init__(self):
        self.connection_list = []
        self.recv_buffer = 128
        self.max_connections = 100
        self.port = 5000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(self.max_connections)
        self.connection_list.append(self.server_socket)
        self.games = {}
        self.statuses = {}
        print('Server started on port ' + str(self.port))
        self.should_stop = False
        signal.signal(signal.SIGTERM, self.stop)
        self.db_path = "zsd_data.db"
        self.db = sqlite3.connect(self.db_path)

    def broadcast_data(self, sock, message):
        for socket in self.connection_list:
            if socket != self.server_socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    disconnect(socket)

    def disconnect(self, socket):
        if socket != self.server_socket:
            del self.games[socket.fileno()]
            del self.statuses[socket.fileno()]
        socket.close()
        self.connection_list.remove(socket)

    def start(self):
        while not self.should_stop:
            read_sockets, write_sockets, error_sockets = select.select(self.connection_list, [], [])

            for sock in read_sockets:
                if sock == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.connection_list.append(sockfd)
                    print('Client (%s, %s) connected' % addr)

                    game = Game(sockfd, self)
                    self.games[sockfd.fileno()] = game
                    self.statuses[sockfd.fileno()] = game.signin()

                else:
                    try:
                        data = sock.recv(self.recv_buffer)
                        if data:
                            if data in [b'\xff\xfb\x01', b'\xff\xfc\x01', b'\xff\xfd\x01', b'\xff\xfe\x01']: continue
                            fileno = sock.fileno()
                            old_status = self.statuses[fileno]
                            if old_status:
                                self.statuses[fileno] = old_status(data.decode())
                            else:
                                self.statuses[fileno] = self.games[fileno].parse_input(data.decode())
                    
                    except UnicodeDecodeError:
                        self.games[sock.fileno()].quit()

        self.stop()
                    

                    # except:
                    #    msg = 'Client (%s, %s) is offline' % addr
                    #    self.broadcast_data(sock, msg) 
                    #    print(msg)
                    #    self.connection_list.remove(sock)

    def stop(self, signum = None, frame = None):
        print("server shutting down")
        self.should_stop = True
        for client in self.connection_list:
            self.disconnect(client)

        self.db.close()

server = Server()

try:
    server.start()
except KeyboardInterrupt:
    server.stop()









