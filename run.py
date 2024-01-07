from flask_socketio import SocketIO

from simulatorui import create_app
from simulatorui.config import config_dict

debug = False
get_config_mode = 'Debug' if debug else 'Production'
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)

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
    print('received subscribe json ' + str(json_subscribe))


@socketio.on('sendrpc', namespace='/simulator')
def sendrpc(json_sendrpc):
    print('received rpc json ' + str(json_sendrpc))


@socketio.on('publish', namespace='/simulator')
def publish(json_publish):
    print('received publish json ' + str(json_publish))


@socketio.on('start-service', namespace='/simulator')
def start_mock_services(jsonapks):
    print('start mock services json ' + str(jsonapks))


@socketio.on("stop_all_mockservices", namespace="/simulator")
def stop_all_mockservices():
    print('stop all mock services ')


if __name__ == '__main__':
    # Run the server
    socketio.run(app, debug=debug)
