import argparse
import threading
from ssh_honeypot import start_server
from app import run

SSH = "ssh"
SSH_DEFAULT_PORT = 2222
WEB = "web"
WEB_DEFAULT_PORT = 8080

ALL = "all"

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[ALL, SSH, WEB],
        required=True
    )
    parser.add_argument(
        "-a",
        "--host",
        type=str,
        default="0.0.0.0"
    )
    parser.add_argument(
        "-s",
        "--ssh-port",
        type=int,
        default=SSH_DEFAULT_PORT
    )
    parser.add_argument(
        "-w",
        "--web-port",
        type=int,
        default=WEB_DEFAULT_PORT
    )

    args = parser.parse_args()

    return args

def start_all_honeypots(host, ssh_port, web_port):
    ssh_thread = threading.Thread(target=start_server, args=(host, ssh_port))
    web_thread = threading.Thread(target=run, args=(host, web_port))

    ssh_thread.start()
    web_thread.start()

if __name__ == "__main__":
    try:
        args = parse_args()

        if args.type == "all":
            print(f"Starting all honeypots on {args.host}\n\tSSH on port {args.ssh_port}\n\tWeb on port {args.web_port}")
            start_all_honeypots(args.host, args.ssh_port, args.web_port)
        elif args.type == SSH:
            print(f"Starting SSH honeypot on {args.host}:{args.ssh_port}")
            start_server(host=args.host, port=args.ssh_port)
        elif args.type == WEB:
            print(f"Starting Web honeypot on {args.host}:{args.web_port}")
            run(host=args.host, port=args.web_port)
        else:
            print("Please specify honeypot type")

    except Exception as e:
        print(e)