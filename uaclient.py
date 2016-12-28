#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente SIP que abre un socket a un servidor
"""

import socket
import sys
import xml.etree.ElementTree as ET


if __name__ == "__main__":
    try:
        CONFIG = str(sys.argv[1])
        METHOD = str(sys.argv[2])
        OPTION = str(sys.argv[3])
    except ValueError:
        sys.exit("Usage: python uaclient.py config method option")

    #TEMA PORT

    tree = ET.parse(CONFIG)
    root = tree.getroot()

    USER = root.find('account').attrib['username']
    PASSWD = root.find('account').attrib['passwd']
    PORT = root.find('uaserver').attrib['port']
    RTPPORT = root.find('rtpaudio').attrib['port']
    PROXYPORT = root.find('regproxy').attrib['port']

    print(USER, PASSWD, PORT, RTPPORT, PROXYPORT)

'''
    INIT = METHOD + ' sip:' + LOGIN + '@' + IP + ' SIP/2.0\r\n\r\n'
    ACK = 'ACK sip:' + LOGIN + '@' + IP + ' SIP/2.0\r\n\r\n'
    BYE = 'BYE sip:' + LOGIN + '@' + IP + ' SIP/2.0\r\n\r\n'

    if (METHOD == 'INVITE'):
        message = INIT
    elif (METHOD == 'BYE'):
        message = BYE

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((IP, PORT))

        my_socket.send(bytes(message, 'utf-8'))
        text = my_socket.recv(1024)
        info = text.decode('utf-8')

        print(info)

        if (info == 'SIP/2.0 100 Trying\r\n\r\n SIP/2.0 ' +
                '180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n'):
            print('Enviamos ACK')
            my_socket.send(bytes(ACK, 'utf-8'))
            text = my_socket.recv(1024)

    print("Socket terminado.")
'''
