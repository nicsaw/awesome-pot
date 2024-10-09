import paramiko
import threading
import socket
import logging
import json
import datetime
import traceback

LOCALHOST = "127.0.0.1"
SSH_PORT = 2222
SSH_BANNER = "SSH-2.0-MySSHServer"
host_key = paramiko.RSAKey(filename="server.key")

logging.basicConfig(level=logging.INFO, format="%(message)s")

def log_event(**kwargs):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "client_ip": kwargs.get('client_ip', None),
        "event_type": kwargs.get('event_type', 'generic_event'),
    }

    extra_fields = {k: v for k, v in kwargs.items() if k not in log_entry}
    log_entry.update(extra_fields)

    logging.info(json.dumps(log_entry))

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.event = threading.Event()
        self.client_ip = client_ip

    def check_channel_request(self, kind, chanid):
        log_event(client_ip=self.client_ip, event_type="check_channel_request", kind=kind)
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        log_event(client_ip=self.client_ip, event_type="get_allowed_auths", username=username)
        return "password"

    # Login attempt
    def check_auth_password(self, username, password):
        log_event(client_ip=self.client_ip, event_type="check_auth_password", username=username, password=password)
        if username != "username" or password != "":
            return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_exec_request(self, channel, command):
        log_event(client_ip=self.client_ip, event_type="check_channel_exec_request", command=command)
        return True

def handle_command(command: bytes, channel: paramiko.Channel, client_ip):
    response = b"\n"
    command = command.strip()

    if command == b"exit":
        channel.close()
    elif command == b"pwd":
        response += b"\\usr\\local\\"
    elif command == b"ls":
        response += b"file1.txt\nfile2.txt\n"
    else:
        response += command

    channel.send(response + b"\r\n")
    print(f"{response = }")
    log_event(client_ip=client_ip, event_type="command", command=command.decode("utf-8").strip(), response=response.decode("utf-8").strip())

def handle_shell_session(channel: paramiko.Channel, client_ip):
    channel.send(b"$ ")
    command = b""
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()

        command += char
        print(f"{command = }")

        if char == b"\r":
            handle_command(command, channel, client_ip)
            channel.send(b"$ ")
            command = b""

def handle_client(client, addr):
    log_event(client_ip=addr[0], event_type="client_connection")

    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        transport.add_server_key(host_key)
        server = SSHServer(addr[0])
        transport.start_server(server=server)

        channel = transport.accept(50)
        if channel is None:
            logging.warning("No channel opened")
            return

        welcome_banner = "Welcome!\r\n"
        channel.send(welcome_banner)

        handle_shell_session(channel, addr[0])
    except Exception as e:
        logging.error(f"ERROR handle_client(): {e}")
        print(traceback.format_exc())
    finally:
        transport.close()

def start_server(host="0.0.0.0", port=SSH_PORT):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(100)
        logging.info(f"Listening on {host}:{port}")

        while True:
            conn, addr = sock.accept()
            logging.info(f"Connection from {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            print(f"Active Connections: {threading.active_count() - 1}")
    except Exception as e:
        logging.error(f"ERROR start_server(): {e}")
        print(traceback.format_exc())
    finally:
        sock.close()

if __name__ == "__main__":
    start_server(LOCALHOST, port=SSH_PORT) # Change later
