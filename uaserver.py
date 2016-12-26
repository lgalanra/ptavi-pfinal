#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor SIP peer2peer
"""

import socketserver
import sys
import os


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
            self.wfile.write(
                b'SIP/2.0 100 Trying\r\n\r\n SIP/2.0 ' +
                b'180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n')
        elif info.startswith('ACK'):
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = './mp32rtp -i 127.0.0.1 -p 23032 < ' + fichero_audio
            print('Vamos a ejecutar', aEjecutar)
            os.system(aEjecutar)
        elif info.startswith('BYE'):
            self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
        else:
            self.wfile.write(b'SIP/2.0 405 Method not Allowed\r\n\r\n')

if __name__ == "__main__":
    try:
        IP = sys.argv[1]
        PORT = int(sys.argv[2])
        fichero_audio = str(sys.argv[3])
    except ValueError:
        print("Usage: python server.py IP port audio_file")
    serv = socketserver.UDPServer(('', PORT), SIPHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
