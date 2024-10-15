from flask import Flask, request, render_template, redirect, url_for
import logging, datetime, json
app = Flask(__name__, template_folder="templates")

logging.basicConfig(level=logging.INFO, format="%(message)s")

def log_event(**kwargs):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        **kwargs
    }

    logging.info(json.dumps(log_entry))

@app.route("/")
def index():
    client_ip = request.remote_addr
    log_event(client_ip=client_ip, event_type="access_index")
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    client_ip = request.remote_addr
    log_event(client_ip=client_ip, event_type="access_register")

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        log_event(client_ip=client_ip, event_type="attempt_register", username=username, email=email, password=password, confirm_password=confirm_password)

        if password != confirm_password:
            return redirect(url_for('register'))

        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    client_ip = request.remote_addr
    log_event(client_ip=client_ip, event_type="access_login")

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        log_event(client_ip=client_ip, event_type="attempt_login", email=email, password=password)

        return redirect(url_for('index'))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
