# awesome-pot

# Installation

```
git clone https://github.com/nicsaw/awesome-pot.git

cd awesome-pot

apt install python3

apt install python3-venv

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

ssh-keygen -t rsa -b 2048 -f server.key
```

# Usage

## Command-line Arguments

| Argument         | Description                                      | Default      |
| ---------------- | ------------------------------------------------ | ------------ |
| `-t, --type`     | Specify the honeypot type (`ssh`, `web`, `all`). | **Required** |
| `-a, --host`     | The host address to bind the honeypots to.       | `0.0.0.0`    |
| `-s, --ssh-port` | Port for the SSH honeypot.                       | `2222`       |
| `-w, --web-port` | Port for the Web honeypot.                       | `8080`       |

## Start All Honeypots

```
python3 honeypot_launcher.py -t all
```

## Start SSH Honeypot:

```
python3 honeypot_launcher.py -t ssh
```

Attacker's POV:

```
ssh -p 2222 user@{IP}
```

## Start Web Honeypot:

```
python3 honeypot_launcher.py -t web
```
