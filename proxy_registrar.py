#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP Register server class
    """
    dicc = {}
    expire = ''
    lists = []
    direction = ''

    def handle(self):
        """
        Método principal para manejar mensajes cliente servidor
        """
        if self.lists == []:
            self.json2registered()

        print(self.client_address)
        request = self.rfile.read().decode('utf-8')
        print(request)
        fields = request.split(' ')

        if fields[0] == 'REGISTER':
            login = fields[1].split(':')
            self.direction = login[1]
            self.dicc[self.direction] = self.client_address[0]
            aux = fields[3].split('\r')

            self.expire = int(aux[0])
            if self.expire == 0:
                del self.dicc[self.direction]

        self.register2json()
        self.wfile.write(b"SIP/2.0 200 OK " + b'\r\n\r\n')
        print(self.dicc)

    def register2json(self):
        """
        Método para almacenar correctamente los datos al json
        """
        exptime = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.gmtime(int(self.expire) + time.time()))
        auxdicc = {'address': self.client_address[0], 'expires': exptime}

        for l in self.lists:
            if l[0] == self.direction:
                self.lists.remove(l)
        self.lists.append([self.direction, auxdicc])

        for l in self.lists:
            if l[1]['expires'] <= time.strftime('%Y-%m-%d %H:%M:%S',
                                                time.gmtime(time.time())):
                self.lists.remove(l)
        json.dump(self.lists, open("registered.json", 'w'),
                  sort_keys=True, indent=4, separators=(',', ': '))

    def json2registered(self):
        """
        Método para comprobar al inicio si ya existía un json
        """
        try:
            self.lists = json.load(open("registered.json", 'r'))
        except:
            pass

if __name__ == "__main__":
    try:
        PORT = int(sys.argv[1])
    except PortError:
        print("Introducir puerto escucha del servidor")
    serv = socketserver.UDPServer(('', PORT), SIPRegisterHandler)
    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
