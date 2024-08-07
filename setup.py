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

import os

from setuptools import find_packages, setup

project_name = "up-simulator"

script_directory = os.path.realpath(os.path.dirname(__file__))
REQUIREMENTS = [i.strip() for i in open(os.path.join("requirements.txt")).readlines()]

setup(
    name=project_name,
    author="Neelam Kushwah",
    author_email="neelam.kushwah@gm.com",
    version="0.1.1-dev",
    python_requires=">=3.8",
    packages=find_packages(),
    package_data={
        'simulator': ['**'],
        'tdk': ['**'],
    },
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license="LICENSE.txt",
    long_description=open("README.adoc").read(),
)
