import argparse
from ssh_honeypot import start_server
from app import run

SSH = "ssh"
SSH_DEFAULT_PORT = 2222
WEB = "web"
WEB_DEFAULT_PORT = 8080

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[SSH, WEB],
        required=True
    )
    parser.add_argument(
        "-a",
        "--host",
        type=str,
        default="0.0.0.0"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int
    )

    args = parser.parse_args()

    if args.port is None:
        args.port = SSH_DEFAULT_PORT if args.type == SSH else WEB_DEFAULT_PORT

    return args

if __name__ == "__main__":
    try:
        args = parse_args()

        if args.type == SSH:
            print(f"Starting SSH honeypot on {args.host}:{args.port}")
            start_server(host=args.host, port=args.port)
        elif args.type == WEB:
            print(f"Starting Web honeypot on {args.host}:{args.port}")
            run(host=args.host, port=args.port)

    except Exception as e:
        print(e)