#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data_breakdown=data.split()
        code = data_breakdown[1]
        return int(code)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    '''
    GET /path/to/resource HTTP/1.1
    Host: www.example.com
    User-Agent: MyHttpClient/1.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Connection: keep-alive
    '''
    '''
    GET /path/to/resource HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: MyHttpClient/1.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nConnection: keep-alive\r\n\r\n
    '''

    def GET(self, url, args=None):
        code = 500
        body = ""
        asked_url=urllib.parse.urlparse(url)
        host = asked_url.hostname
        port = asked_url.port or 80
        path = asked_url.path or '/'
        scheme = asked_url.scheme
        self.connect(host,port)
        request='GET'
        if scheme == 'http' or scheme == 'https':
            request += ' '
            request += path
            request += ' '
            request += 'HTTP/1.1\r\nHost: '
            request += host
            request += '\r\n'
            request += "Connection: close\r\n\r\n"
        self.sendall(request)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        asked_url=urllib.parse.urlparse(url)
        if args:
            body_message = urllib.parse.urlencode(args)
        else:
            body_message = ' '
        host = asked_url.hostname
        port = asked_url.port or 80
        path = asked_url.path or '/'
        scheme = asked_url.scheme
        self.connect(host,port)
        if scheme == 'http' or scheme == 'https':
            request = 'POST ' + path + ' HTTP/1.1\r\nHost: ' + host + '\r\n'
            request += "Content-Length: " + str(len(body_message)) + "\r\n"
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += "Connection: close\r\n\r\n"
            request += str(body_message)
        self.sendall(request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))