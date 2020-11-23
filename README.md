# Skywalking plugins for python

## Installation

```bash
pip install --trusted-host 10.0.162.5 -i http://10.0.162.5:31670 utc-skywalking-plugins
```

## Usage
```python
from skywalking import agent, config, Component
import utc_skywalking_plugins

# start skywalking agent
config.init(collector='cloud.uisee.com:32018', service='test mqtt')
agent.start()
utc_skywalking_plugins.install_emqx()

# than publish and receive message as usual

context = get_context() 
carrier = Carrier()
with context.new_entry_span(op='https://github.com/apache') as span:
    span.component = Component.Unknown
# pass context
_thread_local.context = context

```
