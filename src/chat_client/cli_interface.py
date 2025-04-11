from paho.mqtt.client import Client
import src.common.config as config
from src.common.contract import Message, Action


def print_help():
    print("Chat commands:")
    print("--exit: disconnect from chat")
    print_send_message_help()
    print("--send-file <filepath>: send a file to the user you currently chat with")
    print("--help: show chat commands")

def print_send_message_help():
    print("--chat-with <username>: start direct chat with <username>")
    print("--send-message-to <username>: send message via Server to <username>")


def listen_user_input(mqttc: Client, username: str):
    """
    Process user input: execute commands or send messages or files
    """
    print_help()

    while True:
        command = input()
        if command in ["--exit", "-exit"]:
            break

        elif command in ["--help", "-help"]:
            print_help()

        elif command.startswith("--chat-with") or command.startswith("-chat-with") or command.startswith("chat-with"):
            # Ask server for user's topic. If user is connected server will send the topic and we store it in on_message callback
            command_args = command.split()
            if len(command_args) > 1:
                target_username = command_args[1]
                mqttc.publish(config.SERVER_GET_ADDRESS_TOPIC,
                              Message(Action.GET_ADDRESS, from_username=username, text=target_username).serialize())
            else:
                print("Missing username. Please use the command in format '--chat-with <username>'")

        elif command.startswith("--send-message-to") or command.startswith("-send-message-to") or command.startswith("send-message-to"):
            # Send message to server so it will send it to the end user when the user is connected
            command_args = command.split()
            if len(command_args) > 1:
                target_username = command_args[1]
                msg_text = input(f"Writing to '{target_username}': ")
                # send message for {target_username} to server
                mqttc.publish(config.INDIRECT_MESSAGE_TOPIC_PREFIX + target_username,
                              Message(action = Action.INDIRECT_MESSAGE, from_username=username, text=msg_text).serialize())
            else:
                print("Missing username. Please use the command in format '--send-message-to <username>'")

        elif command.startswith("--send-file") or command.startswith("-send-file") or command.startswith("send-file"):
            # Ask server for user's topic. If user is connected server will send the topic and we store it in on_message callback

            if not current_addressee:
                print("Please first select a user to write to.")
                print("--chat-with <username>: start direct chat with <username>")
                continue

            command_args = command.split()
            if len(command_args) > 1:
                filepath = command_args[1]
                try:
                    with open(filepath, "rb") as f:
                        file_bytes = f.read()
                        mqttc.publish(current_addressee,
                                      Message(Action.DIRECT_SEND_FILE,
                                              from_username=username,
                                              file_bytes=file_bytes,
                                              text=filepath.split("/")[-1]).serialize())
                except FileNotFoundError:
                    print(f"File '{filepath}' not found")
            else:
                print("Missing filepath. Please use the command in format '--send-file <filepath>'")

        else:
            if current_addressee:
                mqttc.publish(current_addressee,
                              Message(Action.DIRECT_MESSAGE, from_username=username, text=command).serialize())
            else:
                print("Please select a user to write to.")
                print_send_message_help()

current_addressee = ""