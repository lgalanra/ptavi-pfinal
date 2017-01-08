#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time
import xml.etree.ElementTree as ET
import random


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

        text = self.rfile.read()
        info = text.decode('utf-8')
        print('Recibimos -> ' + info)

        if info.startswith('REGISTER'):
            self.nonce = ''
            for i in range (10):
                self.nonce += str(random.randint(0,9))
            print(self.nonce)
            self.wfile.write(b'SIP/2.0 401 Unauthorized\r\nWWW Authenticate: \
Digest nonce=' + bytes(self.nonce,'utf-8'))
        else:
            print('Recibimos ->AAAAAAAAAAAAAAAAAAAAAA ')

        




'''
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
'''
if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
        tree = ET.parse(CONFIG)
        root = tree.getroot()
        NAME = root.find('server').attrib['name']
        IP = root.find('server').attrib['ip']
        if IP == '':
            IP = '127.0.0.1'
        else:
            IP = IP
        PORT = root.find('server').attrib['port']
        REGUSERS = root.find('database').attrib['path']
        PASSWDS = root.find('database').attrib['passwdpath']
        LOG = root.find('log').attrib['path']
    except ValueError:
        print("Usage: python proxy_registrar.py config")
    serv = socketserver.UDPServer(('', int(PORT)), SIPRegisterHandler)
    print('Server ' + NAME + ' listening at port ' + PORT + '...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
