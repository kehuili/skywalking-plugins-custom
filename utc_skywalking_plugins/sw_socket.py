from skywalking import Layer, Component
from skywalking.trace import tags
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import get_context
from skywalking.trace.tags import Tag
import json


def install():
    from socket import socket
    _send = socket.send
    _recv = socket.recv
    socket.send = _send_func(_send)
    socket.recv = _recv_func(_recv)


def _send_func(_send):
    def _sw_send(this, data, flags=0):
        peername = this.getpeername()
        peer = '%s:%s' % (peername[0], peername[1])

        context = get_context()
        carrier = Carrier()
        with context.new_exit_span(op="socket" + "/Producer" or "/",
                                   peer=peer, carrier=carrier) as span:
            # no corresponding layer and component
            span.layer = Layer.Unknown
            span.component = Component.Unknown
            payload = {} if data is None else json.loads(str(data, 'utf-8'))
            if 'headers' in payload:
                headers = {}
                for item in carrier:
                    headers[item.key] = item.val
                payload['headers'] = headers
            else:
                payload['headers'] = {}
                for item in carrier:
                    payload['headers'][item.key] = item.val
            payload = json.dumps(payload).encode('utf-8')

            try:
                res = _send(this, payload, flags)
                span.tag(Tag(key='socket.server', val=peer))
            except BaseException as e:
                span.raised()
                raise e
            return res

    return _sw_send


def _recv_func(_recv):
    def _sw_recv(this, bufsize, flags=0):
        context = get_context()
        carrier = Carrier()

        peername = this.getpeername()
        peer = '%s:%s' % (peername[0], peername[1])

        msg = _recv(this, bufsize, flags)
        payload = json.loads(str(msg, 'utf-8'))
        if payload is not None and 'headers' in payload:
            for item in carrier:
                if item.key in payload['headers']:
                    item.val = payload['headers'][item.key]

        with context.new_entry_span(op="socket" + "/Client", carrier=carrier) as span:
            span.layer = Layer.Unknown
            span.component = Component.Unknown

            try:
                span.tag(Tag(key='socket.client', val=peer))
            except BaseException as e:
                span.raised()
                raise e

            return msg

    return _sw_recv
