import paramiko
import threading
import socket
import logging
import json
import datetime

LOCALHOST = "127.0.0.1"
SSH_PORT = 2222

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

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

    def get_allowed_auths(self, username):
        log_event(client_ip=self.client_ip, event_type="get_allowed_auths", username=username)
        return "password"

    # Login attempt
    def check_auth_password(self, username, password):
        log_event(client_ip=self.client_ip, event_type="check_auth_password", username=username, password=password)
        # Accept all logins for now
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_exec_request(self, channel, command):
        log_event(client_ip=self.client_ip, event_type="check_channel_exec_request", command=command)
        return True

# class SSHServer(paramiko.ServerInterface):
#     def __init__(self):
#         self.event = threading.Event()

#     def check_auth_password(self, username, password):
#         logging.info(f"Login attempt - Username: {username}, Password: {password}")
#         return paramiko.AUTH_SUCCESSFUL

#     def check_channel_request(self, kind, chanid):
#         if kind == "session":
#             return paramiko.OPEN_SUCCEEDED
#         return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_client(client):
    try:
        transport = paramiko.Transport(client)
        server = SSHServer()
        transport.start_server(server=server)


    except Exception as e:
        logging.error(f"ERROR handle_client(): {e}")
    finally:
        transport.close()

def start_server(host="0.0.0.0", port=SSH_PORT):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        logging.info(f"Listening on {host}:{port}")

        while True:
            conn, addr = sock.accept()
            logging.info(f"Got connection from {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            print(f"Active Connections: {threading.active_count() - 1}")
    except Exception as e:
        logging.error(f"ERROR: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server(LOCALHOST, SSH_PORT) # Change later
