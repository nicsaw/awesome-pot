from flask import Flask, Request, request, render_template, redirect, url_for, flash, session
import logging, datetime, json, dotenv, os
from user_agents import parse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

dotenv.load_dotenv()

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sap.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO, format="%(message)s", filename="hp-web.log")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(999), nullable=False)
    email = db.Column(db.String(999), unique=True, nullable=False)
    password = db.Column(db.String(999), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    website = db.Column(db.String(999), nullable=False)
    username = db.Column(db.String(999), nullable=False)
    password = db.Column(db.String(999), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<Item(id={self.id}, website={self.website}, username={self.username}, password={self.password}, userID={self.userID})>"

    def to_dict(self):
        return {
            "userID": self.userID,
            "id": self.id,
            "website": self.website,
            "username": self.username,
            "password": self.password
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_event(request: Request, **kwargs):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "client_ip": request.remote_addr,
        "event_type": kwargs.get("event_type", "generic_event"),
        "request_method": request.method,
        "request_path": request.path,
        "request_headers": dict(request.headers),
        "user_agent": str(parse(request.headers.get("User-Agent")))
    }

    extra_fields = {k: v for k, v in kwargs.items() if k not in log_entry}
    log_entry.update(extra_fields)

    print(log_entry)
    logging.info(json.dumps(log_entry))

@app.route("/", methods=["GET", "POST"])
def index():
    log_event(request, event_type=f"access_index_{request.method.upper()}")

    if request.method == "POST":
        website = request.form["website"]
        username = request.form["username"]
        password = request.form["password"]

        if current_user.is_authenticated:
            newItem = Item(
                userID=current_user.id,
                website=website,
                username=username,
                password=password
            )

            db.session.add(newItem)
            db.session.commit()
            log_event(request, event_type=f"item_new", item=newItem.to_dict(), website=website, username=username, password=password)
            return redirect(url_for("index"))
        else:
            flash("You must be logged in to add an item.", "error")
            return redirect(url_for("login"))

    return render_template("index.html", items=Item.query.all())

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    targetItem = Item.query.get_or_404(id)
    log_event(request, event_type=f"item_editing", item=targetItem.to_dict(), website=targetItem.website, username=targetItem.username, password=targetItem.password, id=targetItem.password)
    if request.method == "POST":
        try:
            targetItem.website = request.form["website"]
            targetItem.username = request.form["username"]
            targetItem.password = request.form["password"]
            db.session.commit()
            log_event(request, event_type=f"item_edited", item=targetItem.to_dict(), website=targetItem.website, username=targetItem.username, password=targetItem.password, id=targetItem.password)
            flash(f"Item {targetItem.id} updated", "success")
            return redirect(url_for("index"))
        except Exception as e:
            print(f"ERROR edit({id}): {e}")

    return render_template("edit.html", item=targetItem)

@app.route("/delete/<int:id>")
def delete(id):
    targetItem = Item.query.get_or_404(id)
    try:
        log_event(request, event_type=f"item_delete", item=targetItem.to_dict(), website=targetItem.website, username=targetItem.username, password=targetItem.password, id=targetItem.password)
        db.session.delete(targetItem)
        db.session.commit()
        flash(f"Item {targetItem.id} deleted", "success")
    except Exception as e:
        print(f"ERROR delete({id}): {e}")

    return redirect(url_for("index"))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    search_results = Item.query.filter(Item.website.ilike(f"%{query}%")).all()

    search_results_dict = [item.to_dict() for item in search_results]
    log_event(request, event_type="search", query=query, search_results=search_results_dict)

    return render_template('search.html', query=query, results=search_results)

@app.route("/import_passwords", methods=["GET", "POST"])
def import_passwords():
    log_event(request, event_type="access_import_passwords")

    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.chmod(app.config['UPLOAD_FOLDER'], 0o755)  # Read and execute for owner, read for group and others

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log_event(request, event_type="file_upload", filename=filename, size=file.content_length)

            flash("✅ File uploaded successfully!", "success")
            return redirect(url_for("import_passwords"))

    return render_template("import_passwords.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    log_event(request, event_type="access_register")

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        log_event(
            request,
            event_type="attempt_register",
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        existingUser = User.query.filter_by(email=email).first()
        if existingUser:
            flash("Email already registered!", "error")
            return redirect(url_for("register"))

        newUser = User(username=username, email=email, password=password)
        db.session.add(newUser)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    log_event(request, event_type="access_login")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        log_event(
            request,
            event_type="attempt_login",
            email=email,
            password=password
        )

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host="0.0.0.0", port=8080)
