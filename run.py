from flask_socketio import SocketIO

from flask_migrate import Migrate

from simulatorui import create_app
from simulatorui.config import config_dict

debug = False
get_config_mode = 'Debug' if debug else 'Production'
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)
Migrate(app)

# turn the flask apps into a socketio apps
socketio = SocketIO(app)


@socketio.on("set_utransport", namespace='/simulator')
def set_transport(transport):
    print(transport)


@socketio.on("set_someip_config", namespace='/simulator')
def set_someip_config(localip, multicastip):
    print(localip, multicastip)


@socketio.on("set_zenoh_config", namespace='/simulator')
def set_zenoh_config(routerip):
    print(routerip)


@socketio.on('subscribe', namespace='/simulator')
def subscribe(json_subscribe):
    print('received subscribe json ' + json_subscribe)


@socketio.on('sendrpc', namespace='/simulator')
def sendrpc(json_sendrpc):
    print('received rpc json ' + json_sendrpc)

@socketio.on('publish', namespace='/Portal')
def publish(json_publish):
    print('received publish json ' + json_publish)


if __name__ == '__main__':
    # Run the server
    socketio.run(app, debug=debug)
