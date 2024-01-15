from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol_zenoh.zenoh_utransport import Zenoh

transport = "Zenoh"


class TransportLayer:
    ZENOH = Zenoh()

    def __init__(self):
        if transport == "Zenoh":
            self.instance = self.ZENOH
        else:
            raise ValueError("Unimplemented")

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        return self.instance.invoke_method(topic, payload, attributes)

    def authenticate(self, u_entity: UEntity) -> UStatus:
        return self.instance.authenticate(u_entity)

    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        return self.instance.send(topic, payload, attributes)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.instance.unregister_listener(topic, listener)


if __name__ == "__main__":
    TransportLayer().authenticate(UEntity.EMPTY)
