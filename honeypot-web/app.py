from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    print(f"Accessed index from IP: {request.remote_addr}")
    return render_template("index.html")

@app.route("/register")
def register():
    print(f"Accessed register from IP: {request.remote_addr}")
    return render_template("register.html")

@app.route("/login")
def login():
    print(f"Accessed login from IP: {request.remote_addr}")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
