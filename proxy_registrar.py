#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import socket
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
    nonce = ''

    for i in range(10):
        nonce += str(random.randint(0, 9))

    def handle(self):
        """
        Método principal para manejar mensajes cliente servidor
        """

        text = self.rfile.read()
        info = text.decode('utf-8')
        print('Recibimos -> ' + info)
        self.checkuser_ondate()

        if info.find('Authorization') != -1:
            r = info.split('"')
            response = r[1]

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

            FILE = open('passwords.txt')
            for line in FILE:
                a = line.split(',')
                if self.user == a[0]:
                    self.password = a[1]

            myresponse = str(self.nonce) + str(self.password)
            m = hashlib.sha1()
            m.update(bytes(myresponse, 'utf-8'))
            m2 = m.digest()
            if str(m2) == str(response):
                print('OK, REGISTRADO')

            self.register2json()
        elif info.startswith('INVITE'):

            self.json2registered()

            a = info.split(':')
            b = a[1].split(' ')
            receiver = b[0]
            found = False
            for dicc in self.users:
                if receiver == dicc['address']:
                    found = True
                    global recvIP
                    global recvPORT
                    recvIP = dicc['ip']
                    recvPORT = dicc['port']
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    as my_socket:
                            my_socket.connect((recvIP, int(recvPORT)))

                            print('ENVIANDO: ' + info)
                            my_socket.send(bytes(info, 'utf-8'))

                            text = my_socket.recv(1024)
                            info = text.decode('utf-8')

                            print('RECIBIMOS: ' + info)

                            if info.startswith('SIP/2.0 100 Trying'):
                                print('ENVIAMOS: ' + info)
                                self.wfile.write(bytes(info, 'utf-8'))

            if not found:
                self.wfile.write(b'SIP/2.0 404 User Not Found\r\n\r\n')

        elif info.startswith('ACK'):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                a = info.split(':')
                b = a[1].split(' ')
                receiver = b[0]
                for dicc in self.users:
                    if receiver == dicc['address']:
                        recvIP = dicc['ip']
                        recvPORT = dicc['port']

                my_socket.connect((recvIP, int(recvPORT)))

                print('ENVIANDO: ' + info)
                my_socket.send(bytes(info, 'utf-8'))

        elif info.startswith('BYE'):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                a = info.split(':')
                b = a[1].split(' ')
                receiver = b[0]
                for dicc in self.users:
                    if receiver == dicc['address']:
                        recvIP = dicc['ip']
                        recvPORT = dicc['port']
                my_socket.connect((recvIP, int(recvPORT)))
                print('ENVIANDO: ' + info)
                my_socket.send(bytes(info, 'utf-8'))

                text = my_socket.recv(1024)
                info = text.decode('utf-8')

                print('RECIBIMOS -> ' + info)

                if info.startswith('SIP/2.0 200 OK'):
                    self.wfile.write(bytes(info, 'utf-8'))

        else:
            print(self.nonce)
            self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r\nWWW Authenticate: \
Digest nonce=' + bytes(self.nonce, 'utf-8'))

    def register2json(self):
        """
        Método para almacenar correctamente los datos al json
        """

        if self.users == []:
            self.json2registered()

        auxdicc = {'address': self.user, 'ip': self.ip, 'port': self.port, 'reg\
date': self.regdate, 'expires': self.expire}

        for dicc in self.users:
            if dicc['address'] == self.user:
                self.users.remove(dicc)

        self.users.append(auxdicc)
#        exptime = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtim
# e(int(self.expire) + time.time()))

        self.checkuser_ondate()

        json.dump(self.users, open("registered.json", 'w'),
                  sort_keys=True, indent=4, separators=(',', ': '))

    def checkuser_ondate(self):
        for dicc in self.users:
            if (float(dicc['expires']) + (dicc['regdate'])) <= time.time():
                self.users.remove(dicc)

    def json2registered(self):
        """
        Método para comprobar al inicio si ya existía un json
        """
        try:
            self.users = json.load(open(REGUSERS, 'r'))
        except:
            pass

if __name__ == "__main__":

    recvIP = ''
    recvPORT = 0

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
