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

from uprotocol.uri.factory.uentity_factory import UEntityFactory

logger = logging.getLogger("ServiceUtil")


def get_entity_from_descriptor(entity_descriptor):
    return UEntityFactory.from_proto(entity_descriptor)


def print_subscribe_status(topic, status_code, status_message):
    logger.debug("subscribe_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully subscribed for {topic}")
    else:
        logger.error(
            f"Unsuccessful subscription for {topic} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_publish_status(topic, status_code, status_message):
    logger.debug("publish_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully published for {topic}")
    else:
        logger.error(
            f"Unsuccessful publish for {topic} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_register_rpc_status(methoduri, status_code, status_message):
    logger.debug("register_rpc_status: contents...")
    logger.debug(f"Method uri: {methoduri}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully subscribed for {methoduri}")
    else:
        logger.error(
            f"Unsuccessful subscription for {methoduri} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_create_topic_status_handler(topic, status_code, status_message):
    logger.debug("create_topic_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully Created topic for {topic}")
    else:
        logger.error(
            f"Unsuccessful Creation of topic for {topic} as the status code is {status_code} "
            + f"with status message {status_message}"
        )


class SimulationError(Exception):
    '''
    A generic exception for handling issues with the simulation tool
    '''

    def __init__(self, message="Simulation Error."):
        super().__init__(message)
