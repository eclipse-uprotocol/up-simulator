"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import logging

from uprotocol.v1.uri_pb2 import UUri

from tdk.helper.transport_configuration import TransportConfiguration

# Configure the logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_transport_config():
    """Set the helper config, one time configuration."""
    config = TransportConfiguration()
    config.set_zenoh_config(None,None)  # this will set the zenoh helper

    # config.set_zenoh_config("10.0.0.33", 9090)  # this will set the zenoh helper
    return config


def create_method_uri():
    return UUri(authority_name="Neelam", ue_id=4, ue_version_major=1, resource_id=3)
