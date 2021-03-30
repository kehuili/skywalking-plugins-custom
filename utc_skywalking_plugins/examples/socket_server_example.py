import socket
import json

from skywalking import agent, config
import utc_skywalking_plugins

serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 9999
serversocket.bind((host, port))
serversocket.listen(5)

# start skywalking agent
config.init(collector='cloud.uisee.com:32018', service='testsocket')
agent.start()


while True:
    clientsocket, addr = serversocket.accept()
    peername = clientsocket.getpeername()
    print('address：', addr)
    utc_skywalking_plugins.sk_recv_func(peername, 1024, clientsocket.recv)
    data = {'a':3, 'b':4}
    utc_skywalking_plugins.sk_send_func(peername, data, clientsocket.send)
    # clientsocket.send(json.dumps(data).encode('utf-8'))
    clientsocket.close()
