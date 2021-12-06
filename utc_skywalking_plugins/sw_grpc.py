import grpc
import collections

from skywalking import Layer, Component
from skywalking.trace import tags
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import get_context
from skywalking.trace.tags import Tag

class _ClientCallDetails(
        collections.namedtuple(
            '_ClientCallDetails',
            ('method', 'timeout', 'metadata', 'credentials')),
        grpc.ClientCallDetails):
    pass


class SkyWalkingClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, peer):
        self._peer = peer

    def intercept_unary_unary(self, continuation, client_call_details, request):
        # Add request into client call details, aka, metadata.
        metadata = []
        if client_call_details.metadata is not None:
          metadata = list(client_call_details.metadata)

        context = get_context()

        with context.new_exit_span(op="/Client" + client_call_details.method,
                                    peer=self._peer) as span:
            carrier = span.inject()
            span.layer = Layer.RPCFramework
            span.component = Component.Unknown
            for item in carrier:
                metadata.append((item.key, item.val))

            new_client_call_details = _ClientCallDetails(
                client_call_details.method, client_call_details.timeout, metadata,
                client_call_details.credentials)

            try: 
                response_iterator = continuation(new_client_call_details, request)
                # span.tag(Tag(key=tags.MqBroker, val=peer))
            except BaseException as e:
              span.raised()
              raise e

        return response_iterator

class SkyWalkingServerInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        context = get_context()
        carrier = Carrier()
        metadata = handler_call_details.invocation_metadata
        
        for item in carrier:
            for metadatum in metadata:
                if item.key == metadatum.key:
                    item.val = metadatum.value

        with context.new_entry_span(op="/Server" + handler_call_details.method, carrier=carrier) as span:
            span.layer = Layer.RPCFramework
            span.component = Component.Unknown
            
            try:
                response_iterator = continuation(handler_call_details)
                # span.tag(Tag(key=tags.MqBroker, val=self._peer))
            except BaseException as e:
                span.raised()
                raise e


        return response_iterator