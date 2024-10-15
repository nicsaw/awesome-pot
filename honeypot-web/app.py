from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return redirect(url_for('register'))

        # TODO: Log
        print(username, email, password, confirm_password)

        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # TODO: Log
        print(email, password)

        return redirect(url_for('index'))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
