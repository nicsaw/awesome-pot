from flask import Flask, Request, request, render_template, redirect, url_for
import logging, datetime, json
from user_agents import parse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO, format="%(message)s")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(999), unique=True, nullable=False)
    email = db.Column(db.String(999), unique=True, nullable=False)
    password = db.Column(db.String(999), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<User %r>' % self.username

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

        newUser = User(username=username, email=email, password=password)
        db.session.add(newUser)
        db.session.commit()

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

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template("login.html")

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host="127.0.0.1", port=8080, debug=True)
