from skywalking import Layer, Component
from skywalking.trace import tags
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import get_context, _thread_local
from skywalking.trace.tags import Tag
import json


def install():
    from paho.mqtt.client import Client

    _publish = Client.publish
    __handle_on_message = Client._handle_on_message
    Client.publish = _sw_publish_func(_publish)
    Client._handle_on_message = _sw_on_message_func(__handle_on_message)


def _sw_publish_func(_publish):
    def _sw_publish(this, topic, payload=None, qos=0, retain=False, properties=None):
        from paho.mqtt import __version__
        from packaging import version
        has_properties = False
        # version >= 1.5: has properties as parameter
        if version.parse(__version__) >= version.parse('1.5.0'):
            has_properties = True

        peer = '%s:%s' % (this._host, this._port)

        context = get_context()
        carrier = Carrier()
        import paho.mqtt.client as mqtt
        with context.new_exit_span(op="EMQX/Topic/" + topic + "/Producer" or "/",
                                   peer=peer, carrier=carrier) as span:
            span.layer = Layer.MQ
            span.component = Component.RabbitmqProducer
            # properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH) if properties is None else properties

            # if properties.CorrelationData is None:
            #     headers = {}
            #     for item in carrier:
            #         headers[item.key] = item.val
            #     properties.CorrelationData = headers
            # else:
            #     for item in carrier:
            #         properties.CorrelationData[item.key] = item.val
            payload = {} if payload is None else json.loads(payload)
            if 'headers' in payload:
                headers = {}
                for item in carrier:
                    headers[item.key] = item.val
                payload['headers'] = headers
            else:
                payload['headers'] = {}
                for item in carrier:
                    payload['headers'][item.key] = item.val

            payload = json.dumps(payload)

            try:
                if has_properties:
                    res = _publish(this, topic, payload=payload,
                                   qos=qos, retain=retain, properties=properties)
                else:
                    res = _publish(this, topic, payload=payload,
                                   qos=qos, retain=retain)
                span.tag(Tag(key=tags.MqBroker, val=peer))
                span.tag(Tag(key=tags.MqTopic, val=topic))
            except BaseException as e:
                span.raised()
                raise e
            return res

    return _sw_publish


def _sw_on_message_func(__handle_on_message):
    def _sw_on_message(this, message):
        peer = '%s:%s' % (this._host, this._port)
        context = get_context()
        topic = message.topic
        carrier = Carrier()
        payload = json.loads(str(message.payload, 'utf-8'))
        if payload is not None and 'headers' in payload:
            for item in carrier:
                if item.key in payload['headers']:
                    item.val = payload['headers'][item.key]

        with context.new_entry_span(op="EMQX/Topic/" + topic + "/Consumer" or "", carrier=carrier) as span:
            span.layer = Layer.MQ
            span.component = Component.RabbitmqConsumer
            _thread_local.context = context
            try:
                __handle_on_message(this, message)
                span.tag(Tag(key=tags.MqBroker, val=peer))
                span.tag(Tag(key=tags.MqTopic, val=topic))
            except BaseException as e:
                span.raised()
                raise e

    return _sw_on_message
