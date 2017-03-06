#!/usr/bin/env python3#
# TestServer.py
# -------------------------------

# https://docs.python.org/3.4/reference/simple_stmts.html#grammar-token-assert_stmt

# -------
# imports
# -------

from io       import StringIO
from unittest import main, TestCase

from socket import *

serverName = 'localhost'
serverPort = 2000

def getResponse (request) :
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    clientSocket.send(request.encode())
    modifiedSentence = clientSocket.recv(2048)
    
    response = modifiedSentence.decode()

    clientSocket.close()

    return response

# ------------
# TestTastyTTP
# ------------

class TestServer (TestCase) :

    def test_1_query_1 (self) :
        request = "QUERY\r\n0.0.0.0\r\nEND\r\n"
        response = getResponse(request)
        self.assertEqual("RESULT\r\n0.0.0.0 A 100\r\nEND\r\n", response)

    def test_1_query_2 (self) :
        request = "QUERY\r\n200.34.55.21\r\nEND\r\n"
        response = getResponse(request)
        self.assertEqual("RESULT\r\n200.34.55.21 A 100\r\nEND\r\n", response)

    def test_2_update_1 (self) :
        request = "UPDATE\r\nA 200.34.55.0/24 22\r\nEND\r\n"
        response = getResponse(request)
        self.assertEqual("ACK\r\nEND\r\n", response)

    def test_3_query_1 (self) :
        request = "QUERY\r\n200.34.55.21\r\nEND\r\n"
        response = getResponse(request)
        self.assertEqual("RESULT\r\n200.34.55.21 A 22\r\nEND\r\n", response)

# ----
# main
# ----

if __name__ == "__main__" :
    main()
