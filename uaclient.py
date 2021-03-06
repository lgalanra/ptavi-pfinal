#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente SIP que abre un socket a un servidor
"""

import socket
import sys
import xml.etree.ElementTree as ET
import hashlib
import os
import time


if __name__ == "__main__":
    try:
        CONFIG = str(sys.argv[1])
        METHOD = str(sys.argv[2])
        OPTION = str(sys.argv[3])
    except ValueError:
        sys.exit("Usage: python uaclient.py config method option")

    expires = ''
    tree = ET.parse(CONFIG)
    root = tree.getroot()

    USER = root.find('account').attrib['username']
    PASSWD = root.find('account').attrib['passwd']
    IP = root.find('uaserver').attrib['ip']
    if IP == '':
        IP = '127.0.0.1'
    else:
        IP = IP
    PORT = root.find('uaserver').attrib['port']
    RTPPORT = root.find('rtpaudio').attrib['port']
    PROXYIP = root.find('regproxy').attrib['ip']
    PROXYPORT = root.find('regproxy').attrib['port']
    SONG = root.find('audio').attrib['path']
    LOG = root.find('log').attrib['path']

    if METHOD == 'REGISTER':
        receiver = root.find('regproxy').attrib['ip']
        expires = sys.argv[3]
    elif METHOD == 'INVITE':
        receiver = sys.argv[3]
    elif METHOD == 'BYE':
        receiver = sys.argv[3]
    else:
        sys.exit('Usage: python uaclient.py config method option')

    REGLINE = 'REGISTER sip:' + USER + ':' + PORT + ' SIP/2.0\r\n\r\nExp\
ires: ' + expires + '\r\n\r\n'

    INVLINE = 'INVITE sip:' + receiver + ' SIP/2.0\r\n\r\nContent-Type: applicat\
ion/sdp\r\n\r\nv=0\r\no=' + USER + ' ' + IP + '\r\ns=mysession\r\nt=0\r\nm=\
audio ' + RTPPORT + ' RTP\r\n\r\n'

    ACKLINE = 'ACK sip:' + receiver + ' SIP/2.0\r\n\r\n'
    BYELINE = 'BYE sip:' + receiver + ' SIP/2.0\r\n\r\n'

    if METHOD == 'REGISTER':
        LINE = REGLINE
    elif METHOD == 'INVITE':
        LINE = INVLINE
    elif METHOD == 'BYE':
        LINE = BYELINE

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((PROXYIP, int(PROXYPORT)))

        doc = open(LOG, 'a+')
        doc.write('\r\nStarting...')
        doc.close()
        print('ENVIANDO: ' + LINE)
        my_socket.send(bytes(LINE, 'utf-8'))
        doc = open(LOG, 'a+')
        doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S', time.gmtime(time.time())) + ' Sent to ' + PROXYIP + ':' + PROXYPORT + ':' +
LINE.replace('\r\n', ' '))
        doc.close()

        text = my_socket.recv(1024)
        info = text.decode('utf-8')
        print('RECIBIMOS: ' + info)

        doc = open(LOG, 'a+')
        doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S',time.gmtime(time.time())) + ' Received from ' + PROXYIP + ':' + PROXYPORT + ':' +
info.replace('\r\n',' '))
        doc.close()

        if info.startswith('SIP/2.0 401 Unauthorized'):
            n = info.split('=')
            nonce = n[1]
            response = str(nonce) + str(PASSWD)
            m = hashlib.sha1()
            m.update(bytes(response, 'utf-8'))
            m1 = m.digest()
            my_socket.send(bytes(REGLINE, 'utf-8') + b'Authorization: \
Digest response ="' + bytes(str(m1), 'utf-8') + b'"')
            doc = open(LOG,'a+')
            doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S',time.gmtime(time.time())) + ' Sent to ' + PROXYIP + ':' + PROXYPORT + ':' +
REGLINE.replace('\r\n',' ') +'Authorization: Digest response="' + str(m1) + '"')
            doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S',time.gmtime(time.time())) + ' Received from ' + PROXYIP + ':' +
 PROXYPORT + ':' + 'SIP/2.0 200 OK')
            doc.close()

        elif info.startswith('SIP/2.0 100 Trying'):
            a = info.split(' ')
            RTPPORTrecv2 = a[8]
            b = a[7].split('\r\n')
            RTPIPrecv2 = b[0]

            my_socket.send(bytes(ACKLINE, 'utf-8'))
            doc = open(LOG,'a+')
            doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S',time.gmtime(time.time())) + ' Sent to ' + PROXYIP + ':' + PROXYPORT + ':' +
ACKLINE.replace('\r\n',' '))
            doc.close()
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = './mp32rtp -i ' + RTPIPrecv2 + ' -p\
 ' + str(RTPPORTrecv2) + ' < ' + SONG
            print('Vamos a ejecutar', aEjecutar)
            os.system(aEjecutar)

        elif info.startswith('SIP/2.0 200 OK'):
            print('Fin.')
            doc = open(LOG,'a+')
            doc.write('\r\n' + time.strftime('%Y%m%d%H%M\
%S',time.gmtime(time.time())) + ' Received from ' + PROXYIP + ':' + PROXYPORT +
':' + info.replace('\r\n',' '))
            doc.write('\r\nFinishing...')
            doc.close()
        else:
            pass
