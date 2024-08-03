"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import logging
import time
from datetime import datetime

from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.rpc.rpcmapper import RpcMapper

from simulator.ui.utils.file_utils import save_pub_sub_data, save_rpc_data
from simulator.utils import common_util, constant
from simulator.utils.common_util import flatten_dict
from tdk.core import protobuf_autoloader
from tdk.utils.constant import KEY_URI_PREFIX

total_rpc = 0
success_rpc = 0
logger = logging.getLogger("Simulator")


def rpc_response_handler(socketio, message):
    """
    This callback function get invoked when response received for rpc request
    """
    members = MessageToDict(message, preserving_proto_field_name=True, including_default_value_fields=True)
    socketio.emit(constant.CALLBACK_SENDRPC_RESPONSE, members, namespace=constant.NAMESPACE)


def rpc_logger_handler(socketio, lock_rpc, rpc_request, method_name, json_data, rpcdata):
    global total_rpc, success_rpc
    try:
        rpc_response = MessageToDict(json_data, preserving_proto_field_name=True, including_default_value_fields=True)
        rpc_method_name = method_name
        rpc_request = MessageToDict(rpc_request, preserving_proto_field_name=True, including_default_value_fields=True)

        published_data = ""
        if len(rpcdata) > 0:
            published_data = MessageToDict(
                rpcdata[len(rpcdata) - 1], preserving_proto_field_name=True, including_default_value_fields=True
            )
        total_rpc = total_rpc + 1
        isfailed = True
        if (
            rpc_response.__contains__(constant.KEY_MESSAGE)
            and rpc_response[constant.KEY_MESSAGE].__contains__("OK")
            or rpc_response.__contains__(constant.KEY_CODE)
            and rpc_response[constant.KEY_CODE] == 0
            or rpc_response.__contains__(constant.KEY_STATUS)
            and isinstance(rpc_response[constant.KEY_STATUS], dict)
            and rpc_response[constant.KEY_STATUS][constant.KEY_MESSAGE].__contains__("OK")
            or rpc_response.__contains__(constant.KEY_CODE)
            and isinstance(rpc_response[constant.KEY_CODE], dict)
            and rpc_response[constant.KEY_CODE][constant.KEY_MESSAGE].__contains__("OK")
        ) or method_name == "SayHello":
            success_rpc = success_rpc + 1
            isfailed = False
        failed_rpc = total_rpc - success_rpc
        now = datetime.now()
        dt_string = now.strftime("%d %b, %Y %H:%M:%S")
        json_res = {
            constant.KEY_METHODNAME: rpc_method_name,
            constant.KEY_REQUEST: rpc_request,
            constant.KEY_RESPONSE: rpc_response,
            constant.KEY_DATA: published_data,
            constant.KEY_RPCCOUNT: total_rpc,
            constant.KEY_SUCCESSRPC: success_rpc,
            constant.KEY_FAILEDRPC: failed_rpc,
            constant.KEY_ISFAILED: isfailed,
            constant.KEY_TIME: dt_string,
        }
        save_rpc_data(socketio, lock_rpc, json_res)
    except Exception as ex:
        logger.error("Exception handler:", exc_info=ex)


def subscribe_status_handler(socketio, lock_pubsub, utransport, topic, status_code, status_message):
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")

    if status_code == 0:
        socketio.oldtopic = topic
        json_res = {"type": "Subscribe", "topic": topic, "status": "Success"}
        save_pub_sub_data(socketio, lock_pubsub, json_res)
        message = "Successfully subscribed to " + topic

        if utransport == "ZENOH":
            message = "Successfully subscribed to  " + topic + " to ZENOH"
        socketio.emit(constant.CALLBACK_SUBSCRIBE_STATUS_SUCCESS, message, namespace=constant.NAMESPACE)
    else:
        json_res = {"type": "Subscribe", "topic": topic, "status": "Failed"}
        save_pub_sub_data(socketio, lock_pubsub, json_res)
        socketio.emit(
            constant.CALLBACK_SUBSCRIBE_STATUS_FAILED,
            f"Unsuccessful subscription for {topic} as the status code is {status_code} with "
            f"status message {status_message}",
            namespace=constant.NAMESPACE,
        )


def publish_status_handler(socketio, lock_pubsub, utransport, topic, status_code, status_message, last_published_data):
    if status_code == 0:
        json_res = {
            "type": "Publish",
            "topic": topic,
            "transport": utransport,
            "status": "Success",
            "message": last_published_data,
        }
        save_pub_sub_data(socketio, lock_pubsub, json_res)
        message = "Successfully published message for " + topic
        if utransport == "ZENOH":
            message = "Successfully published message for " + topic + " to ZENOH"
        socketio.emit(constant.CALLBACK_PUBLISH_STATUS_SUCCESS, {"msg": message}, namespace=constant.NAMESPACE)

    else:
        json_res = {
            "type": "Publish",
            "topic": topic,
            "transport": utransport,
            "status": "Failed",
            "message": last_published_data,
        }
        save_pub_sub_data(socketio, lock_pubsub, json_res)
        socketio.emit(
            constant.CALLBACK_PUBLISH_STATUS_FAILED,
            {
                "msg": f"Unsuccessful publish for {topic} as the status code is {status_code} with status message "
                f"{status_message}"
            },
            namespace=constant.NAMESPACE,
        )


def on_receive_event_handler(socketio, lock_pubsub, utransport, topic, payload: UPayload):
    try:
        topic = KEY_URI_PREFIX + topic
        topic_class = protobuf_autoloader.get_topic_map()[topic]
        res = common_util.get_class(topic_class)
        any_message = any_pb2.Any()
        any_message.ParseFromString(payload.value)
        res = RpcMapper.unpack_payload(any_message, res)
        original_members = MessageToDict(res, preserving_proto_field_name=True, including_default_value_fields=True)
        members = flatten_dict(original_members)
        json_res = {
            "type": "OnTopicUpdate",
            "transport": utransport,
            "topic": topic,
            "status": "Success",
            "message": original_members,
        }
        save_pub_sub_data(socketio, lock_pubsub, json_res)

        time.sleep(0.5)
        socketio.emit(
            constant.CALLBACK_ONEVENT_RECEIVE,
            {"json_data": members, "original_json_data": original_members, "topic": topic},
            namespace=constant.NAMESPACE,
        )
    except Exception as ex:
        logger.error("Exception occurs inside onTopicUpdate:", exc_info=ex)
