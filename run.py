from flask_socketio import SocketIO

from flask_migrate import Migrate

from simulatorui import create_app
from simulatorui.config import config_dict

debug = True
get_config_mode = 'Debug' if debug else 'Production'
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)
Migrate(app)

# turn the flask apps into a socketio apps
socketio = SocketIO(app)


@socketio.on("set_utransport", namespace='/simulator')
def set_transport(transport):
    print(transport)


@socketio.on("set_mcu_config", namespace='/Portal')
def set_mcu_config(localip, multicastip):
    print(localip, multicastip)


@socketio.on("set_zenoh_config", namespace='/Portal')
def set_zenoh_config(routerip):
    print(routerip)


if __name__ == '__main__':
    # Run the development server
    socketio.run(app, debug=True)
