import os
import secrets
import sqlite3
import bcrypt
from functools import wraps
from datetime import timedelta
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory, abort
from flask_session import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
REPORT_BASE_DIR = '/home/runner/recon-app'
REPORT_DATA_DIR = os.path.join(REPORT_BASE_DIR, 'data')
DB_PATH = os.path.join(BASE_DIR, 'user_auth.db')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(24))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(BASE_DIR, '.flask_session')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
Session(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Missing credentials"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            session.clear()
            session['user_id'] = user[0]
            session['email'] = email
            session.permanent = True
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"status": "error", "message": "Internal error."}), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route('/<path:report_name>')
@login_required
def view_report(report_name):
    if '/' in report_name or '..' in report_name:
        return render_template("404.html"), 404
    filename = f"{report_name}.html"
    full_path = os.path.join(REPORT_BASE_DIR, filename)
    if not os.path.isfile(full_path):
        return render_template("404.html"), 404
    return send_from_directory(REPORT_BASE_DIR, filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route('/api/check-session')
def check_session():
    if 'user_id' in session:
        return jsonify({'active': True})
    return jsonify({'active': False}), 401