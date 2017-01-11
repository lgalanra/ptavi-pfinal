#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor SIP peer2peer
"""

import socketserver
import sys
import os
import xml.etree.ElementTree as ET


class SIPHandler(socketserver.DatagramRequestHandler):

    """
    Clase para servidor SIP p2p
    """

    def handle(self):
        """
        Método principal para manejar mensajes cliente servidor
        """
        text = self.rfile.read()
        info = text.decode('utf-8')
        print('Recibimos -> ' + info)

        if info.startswith('INVITE'):
            a = info.split(' ')
            global RTPPORTrecv
            RTPPORTrecv = a[5]

            b = a[4].split('\r\n')
            global RTPIPrecv
            RTPIPrecv = b[0]

            inviteresp = 'SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 \
Ring\r\n\r\nSIP/2.0 200 OK\r\n\r\n'
            sdp = 'Content-Type: application/sdp\r\n\r\nv=0\r\no=' + USER + ' ' + IP + '\r\ns=mysession2\r\nt=0\r\nm=audio ' + RTPPORT + ' RTP\r\n\r\n'

            self.wfile.write(bytes(inviteresp + sdp, 'utf-8'))

        elif info.startswith('ACK'):
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = './mp32rtp -i ' + RTPIPrecv + ' -p ' + str(RTPPORTrecv) + ' < ' + SONG
            print('Vamos a ejecutar', aEjecutar)
            os.system(aEjecutar)
        elif info.startswith('BYE'):
            self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
        else:
            self.wfile.write(b'SIP/2.0 405 Method not Allowed\r\n\r\n')

if __name__ == "__main__":

    RTPIPrecv = ''
    RTPPORTrecv = 0

    try:
        CONFIG = sys.argv[1]
        tree = ET.parse(CONFIG)
        root = tree.getroot()
        USER = root.find('account').attrib['username']
        IP = root.find('uaserver').attrib['ip']
        if IP == '':
            IP = '127.0.0.1'
        else:
            IP = IP
        PORT = root.find('uaserver').attrib['port']
        RTPPORT = root.find('rtpaudio').attrib['port']
        SONG = root.find('audio').attrib['path']

    except ValueError:
        print("Usage: python uaserver.py config")
    serv = socketserver.UDPServer(('', int(PORT)), SIPHandler)
    print("Listening...")

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
