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

# SSH Honeypot

Start SSH Honeypot:

```
python3 ssh_honeypot.py
```

Attacker's POV:

```
ssh -p 2222 user@{IP}
```

# Web Honeypot

Start Web Honeypot:

```
python3 app.py
```
