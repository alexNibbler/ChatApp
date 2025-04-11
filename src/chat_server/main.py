import src.common.config as config
from src.common.contract import Message, Action
import paho.mqtt.client as mqtt

db_users = {}
db_messages = {}

# The callback for the client upon receiving a CONNACK response from the server.
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print(f"Connected to chat: {reason_code}")
    client.subscribe(config.SERVER_CONNECT_TOPIC)
    client.subscribe(config.SERVER_GET_ADDRESS_TOPIC)
    client.subscribe(f"{config.INDIRECT_MESSAGE_TOPIC_PREFIX}#")

def on_message(client: mqtt.Client, userdata, msg):
    msg_obj = Message.deserialize(msg.payload)
    if msg.topic == config.SERVER_CONNECT_TOPIC:
        # Once user is connected server stores user's topic in db_users
        username = msg_obj.from_username
        print(f"{username} connected")
        if username not in db_users:
            db_users[username] = config.USER_TOPIC_PREFIX + username

        # if there are messages waiting for the user - send them
        if username in db_messages:
            for stored_message in db_messages[username]:
                client.publish(db_users[username], stored_message)
            db_messages.pop(username)

    elif msg.topic == config.SERVER_GET_ADDRESS_TOPIC:
        # If user is connected - return topic, if not - notification that user is not connected
        target_username = msg_obj.text
        if target_username in db_users:
            response = Message(Action.GET_ADDRESS, from_username=target_username, text=db_users[target_username])
            from_username = msg_obj.from_username
            client.publish(db_users[from_username], response.serialize())
        else:
            response = Message(Action.GET_ADDRESS, from_username=target_username, text=f"User {target_username} is not connected")
            from_username = msg_obj.from_username
            client.publish(db_users[from_username], response.serialize())

    elif msg.topic.startswith("/chatapp/send_to_server/"):
        # if user is connected - send message immediately
        # if user is not connected - save message to be sent upon connection
        to_username = msg.topic.split("/")[-1]
        if to_username in db_users:
            client.publish(db_users[to_username], msg.payload)
        else:
            q = db_messages.get(to_username)
            if q is None:
                db_messages[to_username] = list()
            db_messages[to_username].append(msg.payload)

def on_log(client, userdata, level, buff):
    if level == mqtt.LogLevel.MQTT_LOG_ERR:
        print(buff)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_log = on_log

mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
mqttc.loop_forever()