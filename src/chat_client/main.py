import paho.mqtt.client as mqtt
from src.common.contract import Message, Action
import src.chat_client.cli_interface as cli
import src.common.config as config

# The callback for the client upon receiving a CONNACK response from the server.
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print(f"Connected to chat: {reason_code}")
    client.subscribe(config.USER_TOPIC_PREFIX + username)
    client.publish(config.SERVER_CONNECT_TOPIC, Message(Action.CONNECT, from_username=username).serialize())

def on_message(client, userdata, msg):
    msg_obj = Message.deserialize(msg.payload)

    if msg_obj.action == Action.CONNECT:
        # Handler for server response on connect. Currently, server doesn't response
        pass
    elif msg_obj.action == Action.GET_ADDRESS:
        # If server replies with a topic we use it for 'direct' communication.
        # If server's response is not a topic - print it, it's probably error message
        if msg_obj.text.startswith("/chatapp"):
            cli.current_addressee = msg_obj.text
            target_username = msg_obj.from_username
            print(f"Writing to '{target_username}'")
        else:
            print(msg_obj.text)
    elif msg_obj.action == Action.DIRECT_SEND_FILE:
        # Receive file
        title = msg_obj.text
        if not title:
            title = "received_file"
        try:
            with open(f"downloads/{title}", "wb") as f:
                f.write(msg_obj.file_bytes)
            print("File received and saved.")
        except Exception as ex:
            print(f"File could not be saved: {ex}")
    else:
        # just a message, print it
        print(f"{msg_obj.from_username}: {msg_obj.text}")


def on_log(client, userdata, level, buff):
    if level == mqtt.LogLevel.MQTT_LOG_ERR:
        print(buff)

username = input("Welcome to the chat! Please enter your username to log in: ")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_log = on_log

mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
mqttc.loop_start()

# wait for user input
cli.listen_user_input(mqttc, username)

mqttc.disconnect()
mqttc.loop_stop()