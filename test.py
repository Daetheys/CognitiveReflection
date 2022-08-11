import numpy as np


class AbstractServer:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def __str__(self):
        return "Server: {}, IP: {}, Port: {}".format(self.name, self.ip, self.port)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name and self.ip == other.ip and self.port == other.port

    def __hash__(self):
        return hash(self.name) ^ hash(self.ip) ^ hash(self.port)


    

        




