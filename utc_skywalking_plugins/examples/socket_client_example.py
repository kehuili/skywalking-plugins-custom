import socket

from skywalking import agent, config
import utc_skywalking_plugins

serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

port = 9999


# start skywalking agent
config.init(collector='cloud.uisee.com:32018', service='testsocket')
agent.start()

# receive message as usual
# serversocket.connect((host, port))
# msg = serversocket.recv(1024)


serversocket.connect(('localhost', port))
msg = {'a': 'Hello World'}
# send message as usual
peername = serversocket.getpeername()
utc_skywalking_plugins.sk_send_func(peername, msg, serversocket.send)
# clientsocket.send(msg.encode('utf-8'))
serversocket.close()
