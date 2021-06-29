# Skywalking plugins for python

## Installation

```bash
pip install --trusted-host 10.0.162.5 -i http://10.0.162.5:31670 utc-skywalking-plugins
```

## Usage
```python
from skywalking import agent, config, Component
from skywalking.trace.context import get_context
import utc_skywalking_plugins

# start skywalking agent
config.init(collector='cloud.uisee.com:32018', service='test mqtt')
agent.start()

# install mqtt plugin
utc_skywalking_plugins.install_mqtt()
# install skywalking plugin
utc_skywalking_plugins.install_socket()

# than publish and receive message as usual

### create a local span
context = get_context() 
span = context.new_local_span(op='start')
span.start()
span.tag(Tag(key='Singer', val='Nakajima'))
# do something
span.stop()

# or
context = get_context() 
with context.new_local_span(op='start') as span:
    span.tag(Tag(key='Singer', val='Nakajima'))
# when use 'with' syntax, will automatically start span when enter the 'with' context, stop when exit

### cross thread propagation
@runnable()
def some_method(): 
    # do something

from threading import Thread 
t = Thread(target=some_method)
t.start()

```
