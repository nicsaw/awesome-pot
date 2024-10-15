from flask import Flask, Request, request, render_template, redirect, url_for
import logging, datetime, json
from user_agents import parse

app = Flask(__name__, template_folder="templates")

logging.basicConfig(level=logging.INFO, format="%(message)s")

def log_event(request: Request, **kwargs):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "client_ip": request.remote_addr,
        "event_type": kwargs.get("event_type", "generic_event"),
        "request_method": request.method,
        "request_path": request.path,
        "request_headers": dict(request.headers),
        "user_agent": str(parse(request.headers.get('User-Agent')))
    }

    extra_fields = {k: v for k, v in kwargs.items() if k not in log_entry}
    log_entry.update(extra_fields)

    logging.info(json.dumps(log_entry))

@app.route("/")
def index():
    log_event(request, event_type="access_index")
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    log_event(request, event_type="access_register")

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        log_event(
            request,
            event_type="attempt_register",
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )

        if password != confirm_password:
            return redirect(url_for('register'))

        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    log_event(request, event_type="access_login")

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        log_event(
            request,
            event_type="attempt_login",
            email=email,
            password=password
        )

        return redirect(url_for('index'))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
