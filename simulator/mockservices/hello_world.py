# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

from datetime import datetime
from threading import Thread

from google.protobuf.json_format import MessageToDict
from google.protobuf.text_format import MessageToString
from google.type.timeofday_pb2 import TimeOfDay

from simulator.core.abstract_service import BaseService
from simulator.utils.constant import KEY_URI_PREFIX
from target.protofiles.example.hello_world.v1.hello_world_topics_pb2 import Timer


class HelloWorldService(BaseService):
    """
    The HelloWorldService object handles mock services for the hello-world service.
    This service contains 1 RPC method called "SayHello". This RPC method accepts a
    HelloRequest message and returns a HelloResponse message. The protobuf is defined as follows:

    service HelloWorld {
      option (name) = "example.hello_world";

      // Say Hello method
      rpc SayHello(HelloRequest) returns (HelloResponse) { option (method_id) = 1; }
    }

    // The request message containing the user's name.
    message HelloRequest { string name = 1; }

    // The response message containing the greetings
    message HelloResponse { string message = 1; }
    """

    def __init__(self, portal_callback=None):
        """
        Mock service constructor. Specify the service name to the parent constructor.
        """
        super().__init__("example.hello_world", portal_callback)

    def start_publishing(self):
        timer_pub_thread = Thread(target=self.PublishTimerMessage(), daemon=True)
        timer_pub_thread.start()

    # The UltifiLink.RequestListener decorator is used to define an RPC
    # handler. This decorator registers the method by using the method name.
    # The method must have same name as the RPC method.
    # When an rpc call is made for this
    # method, this method will be called with the protobuf object
    # for the rpc request (a HelloRequest message in this case),
    # and a protobuf object for the rpc
    # response (a HelloResponse message).
    # The response object will be sent to the caller as the RPC response
    # after it returns from this method.
    @BaseService.RequestListener
    def SayHello(self, request, response):
        """
        Handles SayHello RPC calls. This method is called whenever a SayHello
        RPC call is invoked. It is called with two parameters: request and response.
        request is an HelloRequest protobuf object, and response is a HelloResponse
        protobuf object.
        """
        print("SayHello RPC method has been invoked.")
        print(f"Received the following request of type {type(request)}:")
        print(MessageToString(request))
        # read the name from the request
        name = request.name
        # set the response message
        response.message = f"Hello {name}!"
        # return the response
        print(f"Returning the following response of type {type(response)}:")
        print(MessageToString(response))
        return response

    def PublishTimerMessage(service):
        """
        Publishes a Timer message based on the current timestamp after every second and every minute
        """
        # Create a TimeOfDay instance
        time_of_day = TimeOfDay()
        one_sec_topic = KEY_URI_PREFIX + "/example.hello_world/1/one_second#Timer"
        one_min_topic = KEY_URI_PREFIX + "/example.hello_world/1/one_minute#Timer"

        while True:
            # Get current time
            current_time = datetime.now().time()

            # Set the time fields
            time_of_day.hours = current_time.hour

            if time_of_day.seconds != current_time.second:
                time_of_day.seconds = current_time.second
                if time_of_day.minutes != current_time.minute:
                    time_of_day.minutes = current_time.minute
                    # publish one minute topic with payload every minute
                    service.publish(one_min_topic, MessageToDict(Timer(time=time_of_day)))
                # publish one second topic with payload every second
                service.publish(one_sec_topic, MessageToDict(Timer(time=time_of_day)))
