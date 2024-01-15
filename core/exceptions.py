# Copyright (C) GM Global Technology Operations LLC 2022-2023.
# All Rights Reserved.
# GM Confidential Restricted.


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


class SimulationError(Exception):
    '''
    A generic exception for handling issues with the simulation tool
    '''

    def __init__(self, message="Simulation Error."):
        super().__init__(message)
