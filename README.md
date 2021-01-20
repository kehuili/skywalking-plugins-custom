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

context = get_context() 
carrier = Carrier()
with context.new_entry_span(op='https://github.com/apache', carrier=carrier) as span:
    span.component = Component.Unknown

```
