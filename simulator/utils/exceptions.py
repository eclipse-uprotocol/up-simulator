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


class ValidationError(Exception):
    '''
    A generic exception for handling issues with protobuf data validation
    '''

    def __init__(self, code, message="Validation Error."):
        self.code = code
        self.message = message
        super().__init__(self.message)


class GeofencingError(Exception):
    '''
    A generic exception for handling geofencing issues with protobuf data validation
    '''

    def __init__(self, value):
        self.value = value
        super().__init__(self.value)


class AndroidError(Exception):
    '''
    A generic exception for handling issues with the android emulator
    '''

    def __init__(self, message="Emulator Error."):
        super().__init__(message)
