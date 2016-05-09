#!/usr/bin/env python3

import socket, select, sys, os

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
        print('Server started on port ' + str(self.port))

    def broadcast_data(self, sock, message):
        for socket in self.connection_list:
            if socket != self.server_socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    disconnect(socket)

    def disconnect(self, socket):
        del self.games[socket.fileno()]
        socket.close()
        self.connection_list.remove(socket)

    def start(self):
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.connection_list, [], [])

            for sock in read_sockets:
                if sock == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.connection_list.append(sockfd)
                    print('Client (%s, %s) connected' % addr)

                    game = Game(sockfd, self)
                    self.games[sockfd.fileno()] = game
                    game.start()

                else:
                    try:
                        data = sock.recv(self.recv_buffer)
                        if data:
                            self.games[sock.fileno()].parse_input(data.decode())
                    
                    except UnicodeDecodeError:
                        self.games[sock.fileno()].quit()
                    

                    # except:
                    #    msg = 'Client (%s, %s) is offline' % addr
                    #    self.broadcast_data(sock, msg) 
                    #    print(msg)
                    #    self.connection_list.remove(sock)

server = Server()

server.start()

print('(This is a debug statement)')








