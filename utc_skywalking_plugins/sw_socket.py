import json

from skywalking import Layer, Component
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import get_context, _thread_local
from skywalking.trace.tags import Tag



def sk_send_func(peername, data, func, flags=0):
    peer = '%s:%s' % (peername[0], peername[1])
    context = get_context()
    carrier = Carrier()
    with context.new_exit_span(op="socket" + "/Producer" or "/",
                               peer=peer, carrier=carrier) as span:
        # no corresponding layer and component
        span.layer = Layer.Unknown
        span.component = Component.Unknown
        # payload = {} if data is None else json.loads(str(data, 'utf-8'))
        payload = {} if data is None else data
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
            res = func(payload, flags)
            span.tag(Tag(key='socket.server', val=peer))
        except BaseException as e:
            span.raised()
            raise e
        return res

def sk_recv_func(peername, bufsize, func, flags=0):
    context = get_context()
    carrier = Carrier()
    peer = '%s:%s' % (peername[0], peername[1])

    msg = func(bufsize, flags)
    payload = json.loads(str(msg, 'utf-8'))
    if payload is not None and 'headers' in payload:
        for item in carrier:
            if item.key in payload['headers']:
                item.val = payload['headers'][item.key]

    with context.new_entry_span(op="socket" + "/Client", carrier=carrier) as span:
        span.layer = Layer.Unknown
        span.component = Component.Unknown
        # _thread_local.context = context

        try:
            span.tag(Tag(key='socket.client', val=peer))
        except BaseException as e:
            span.raised()
            raise e

        return msg
