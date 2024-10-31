import argparse
import subprocess

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

        if args.type == WEB:
            print(f"Starting Web honeypot on {args.host}:{args.port}")
            subprocess.run(["python3", "app.py"])
        elif args.type == SSH:
            print(f"Starting SSH honeypot on {args.host}:{args.port}")
            subprocess.run(["python3", "ssh_honeypot.py"])

    except Exception as e:
        print(e)