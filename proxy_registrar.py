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
import hashlib
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP Register server class
    """
    dicc = {}
    expire = ''
    users = []
    direction = ''
    nonce = ''
    for i in range (10):
        nonce += str(random.randint(0,9))

# OJO! CAMBIAR NONCE PARA CADA USUARIO


    def handle(self):
        """
        Método principal para manejar mensajes cliente servidor
        """

        text = self.rfile.read()
        info = text.decode('utf-8')
        print('Recibimos -> ' + info)


        if info.find('Authorization') != -1:
            print('VAMOS A COMPROBAAAAAAAAR ')
            r = info.split('"')
            response = r[1]
            print('ESTO ES EL RESPONSE: ' + response)

            print('Y ESTO EL NONCE QUE TENÍA: ' + self.nonce)


            data = info.split(':')

            self.user = data[1]
            self.ip = self.client_address[0]
            print(self.ip)
            p = data[2].split(' ')
            self.port = p[0]
            self.regdate = time.time()

            e = data[3].split('\r\n')
            e1 = e[0].split(' ')
            self.expire = e1[1]


            self.register2json()

            print(self.user + 'UEEEEEEEEEEEEEEEEEEE')
            FILE = open('passwords.txt')
            for line in FILE:
                miau = line.split(',')
                print(miau)
                if self.user == miau[0]:
                    print('SÍ QUE ESTÁ\r\n')
                    self.password = miau[1]
                    print(self.password)
                print('LÍNEA DEL ARCHIVO')

            myresponse = str(self.nonce) + str(self.password)
            m = hashlib.sha1()
            m.update(bytes(myresponse,'utf-8'))
            m2 = m.digest()
            print(m2)
            print(response)
            if str(m2) == str(response):
                print('ESTÁ')
#                register2json()

        else:
            print(self.nonce)
            self.wfile.write(b'SIP/2.0 401 Unauthorized\r\nWWW Authenticate: \
Digest nonce=' + bytes(self.nonce,'utf-8'))

    def register2json(self):
        """
        Método para almacenar correctamente los datos al json
        """

        auxdicc = {'address': self.user, 'ip': self.ip, 'port': self.port,'regdate': self.regdate, 'expires': self.expire}

#        for i in self.users:
#            if i['address'] == self.direction:
#                self.users.remove(l)

        self.users.append(auxdicc)
        exptime = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(int(self.expire) + time.time()))

#        for l in self.users:
#            if l[1]['expires'] <= time.strftime('%Y-%m-%d %H:%M:%S',
#                                                time.gmtime(time.time())):
#            self.users.remove(l)

        json.dump(self.users, open("registered.json", 'w'),
                  sort_keys=True, indent=4, separators=(',', ': '))


'''
        if self.users == []:
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


    def json2registered(self):
        """
        Método para comprobar al inicio si ya existía un json
        """
        try:
            self.users = json.load(open(REGUSERS, 'r'))
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
