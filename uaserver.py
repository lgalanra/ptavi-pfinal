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
            print(a)
            global RTPPORTrecv
            RTPPORTrecv = a[5]
            print(RTPPORTrecv)

            b = a[4].split('\r\n')
            global RTPIPrecv
            RTPIPrecv = b[0]
            print(RTPIPrecv)

            print('IP Y PUERTO RTP EXTRAÍDOS!!!!!!!')
            self.wfile.write(
                b'SIP/2.0 100 Trying\r\n\r\n SIP/2.0 ' +
                b'180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n')



        elif info.startswith('ACK'):
            print('YIIIIIIIIHAAAAAAAAAAAAAAAAAACK')
            print(SONG)
            print('VAMOS A MANDAR CANCIÓN A: ' + RTPIPrecv + ' ' + str(RTPPORTrecv))
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = './mp32rtp -i ' + RTPIPrecv + ' -p ' + str(RTPPORTrecv) + ' < ' + SONG
            print('Vamos a ejecutar', aEjecutar)
            os.system(aEjecutar)
            print('EJECUTADO!')
        elif info.startswith('BYE'):
            print('RECIBIDO BYE! MANDO 200 OK')
            self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
        else:
            pass #self.wfile.write(b'SIP/2.0 405 Method not Allowed\r\n\r\n')

if __name__ == "__main__":

    RTPIPrecv = ''
    RTPPORTrecv = 0

    try:
        CONFIG = sys.argv[1]
        tree = ET.parse(CONFIG)
        root = tree.getroot()
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

    print(IP,PORT,RTPPORT)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
