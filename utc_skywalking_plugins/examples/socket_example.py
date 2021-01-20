import socket
import sys
import json
from skywalking import agent, config

import utc_skywalking_plugins

serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9999
serversocket.bind((host, port))
serversocket.listen(5)

# start skywalking agent
config.init(collector='cloud.uisee.com:32018', service='testsocket')
agent.start()
utc_skywalking_plugins.install_socket()

# receive message as usual
# serversocket.connect((host, port))
# msg = serversocket.recv(1024)

clientsocket, addr = serversocket.accept()
msg = json.dumps({'a': 'Hello World'})
# send message as usual
clientsocket.send(msg.encode('utf-8'))
clientsocket.close()
