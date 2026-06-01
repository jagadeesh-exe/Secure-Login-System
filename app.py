from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "secure_secret_key"

# Create database
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password BLOB
)
""")
conn.commit()
conn.close()

register_page = """
<h2>Register</h2>
<form method="post">
Username: <input name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<button type="submit">Register</button>
</form>
<a href="/login">Login</a>
"""

login_page = """
<h2>Login</h2>
<form method="post">
Username: <input name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<button type="submit">Login</button>
</form>
<a href="/">Register</a>
"""

dashboard_page = """
<h2>Welcome {{user}}</h2>
<a href="/logout">Logout</a>
"""

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3 or len(password) < 6:
            return "Invalid input"

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template_string(register_page)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user[0]):
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template_string(login_page)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template_string(
        dashboard_page,
        user=session["user"]
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)