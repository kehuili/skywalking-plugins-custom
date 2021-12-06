# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import logging

import grpc

import time
from skywalking import agent, config
import helloworld_pb2
import helloworld_pb2_grpc
import utc_skywalking_plugins

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    sw_interceptor = utc_skywalking_plugins.SkyWalkingClientInterceptor('localhost:50051')
    with grpc.insecure_channel('localhost:50051') as channel:
        channel = grpc.intercept_channel(channel, sw_interceptor)
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)
    time.sleep(10)

if __name__ == '__main__':
    # start skywalking agent
    config.init(collector='cloud.uisee.com:30363', service='grpcclient')
    agent.start()
    logging.basicConfig()
    run()
