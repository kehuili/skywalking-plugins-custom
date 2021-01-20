import paho.mqtt.client as mqtt
from skywalking import agent, config, Component
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import SpanContext, get_context, _thread_local
import json
import utc_skywalking_plugins

#Connection success callback
def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))

# Message receiving callback
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# start skywalking agent
# publish: create exit span
# receive: create entry span
config.init(collector='cloud.uisee.com:32018', service='test mqtt')
agent.start()
# install emqx skywalking plugin
utc_skywalking_plugins.install_mqtt()

# pass an existing context
context = get_context() 
carrier = Carrier()
with context.new_entry_span(op='test') as span:
    span.component = Component.Unknown
_thread_local.context = context

client = mqtt.Client()

# Specify callback function
client.on_connect = on_connect
client.on_message = on_message

# Establish a connection
client.connect('127.0.0.1', 1883, 60)
# Publish a message
client.publish('emqtt',payload=json.dumps({'a': 'Hello World'}),qos=0)

client.loop_forever()