"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import os.path

REPO_URL = "https://github.com/COVESA/uservices.git"
TAG_NAME = "f42900216f9c3b92147a1b0c14697262f8811ab3"
PROTO_REPO_DIR = os.path.join("tdk", "target", "protos")
PROTO_OUTPUT_DIR = os.path.join("tdk", "target", "protofiles")
RESOURCE_CATALOG_DIR = os.path.join("tdk", "target", "resource_catalog")

RESOURCE_CATALOG_CSV_NAME = "resource_catalog.csv"
RESOURCE_CATALOG_JSON_NAME = "resource_catalog.json"

KEY_PROTO_ENTITY_NAME = "uprotocol"
KEY_URI_PREFIX = "up:"
