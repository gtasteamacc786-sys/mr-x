from flask import Flask, request, render_template_string, redirect, url_for, session
import threading
import time
import requests
import uuid
import random
from platform import system
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_strong_secret_key_here_Change_This_In_Production'

# Multi-User Credentials (Username: Password)
USER_CREDENTIALS = {
    "admin": "5550561",
    "sameer": "sameer123",
    "ali": "ali456",
    "ahmed": "ahmed789", 
    "zain": "zain101",
    "hamza": "hamza202",
    "usman": "usman303",
    "bilal": "bilal404"
}

# User roles and permissions
USER_ROLES = {
    "admin": "admin",  # Full access
    "sameer": "admin", # Full access
    "ali": "user",
    "ahmed": "user", 
    "zain": "user",
    "hamza": "user",
    "usman": "user",
    "bilal": "user"
}

# Constants for colors and formatting
RED = '\033[1;31m'
BLUE = "\033[1;34m"
WHITE = "\033[1;37m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
GREEN = "\033[1;32m"
RESET = "\033[0m"

# Abuse keywords list (customize as needed)
ABUSE_KEYWORDS = ['abuseword1', 'abuseword2', 'badword']

# In-memory data stores
tasks = {}  # task_id -> task info
accounts = {}  # token -> account info
task_threads = {}  # task_id -> thread object
task_stop_events = {}  # task_id -> threading.Event()
chat_logs = []  # Store chat logs with timestamps
server_start_time = datetime.now()  # Server start time
user_sessions = {}  # username -> session info

# Free IP geolocation API (replace with paid for production)
GEO_API_URL = "http://ip-api.com/json/"

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        if USER_ROLES.get(session.get('username')) != 'admin':
            return redirect(url_for('index', error="Admin access required!"))
        return f(*args, **kwargs)
    return decorated_function

# Login HTML template (Updated for multi-user)
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <title>UNDER COVER BOYS SERVER - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet" />
    <style>
        body {
            margin: 0; padding: 15px;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(-45deg, #7b2ff7, #f107a3, #17ead9, #6078ea);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #fff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        @keyframes gradientBG {
            0% {background-position:0% 50%;}
            50% {background-position:100% 50%;}
            100% {background-position:0% 50%;}
        }
        .login-container {
            max-width: 450px;
            width: 100%;
            background: rgba(0,0,0,0.85);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            font-weight: 700;
            font-size: 2rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f107a3, #7b2ff7, #17ead9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1rem;
            color: #ccc;
        }
        .users-list {
            background: rgba(123,47,247,0.2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }
        .users-list h3 {
            margin-top: 0;
            color: #17ead9;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            font-size: 1rem;
            background: linear-gradient(90deg, #17ead9, #f107a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        input[type=text], input[type=password] {
            width: 100%;
            padding: 14px 12px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 500;
            color: #222;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: box-shadow 0.3s ease, transform 0.2s ease;
            box-sizing: border-box;
        }
        input[type=text]:focus, input[type=password]:focus {
            outline: none;
            box-shadow: 0 0 12px #f107a3;
            transform: scale(1.02);
        }
        button {
            width: 100%;
            background: linear-gradient(90deg, #f107a3, #7b2ff7);
            color: white;
            font-size: 1.3rem;
            font-weight: 700;
            padding: 16px 0;
            border: none;
            border-radius: 14px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(241,7,163,0.6);
            transition: background 0.4s ease, box-shadow 0.4s ease, transform 0.2s ease;
        }
        button:hover {
            background: linear-gradient(90deg, #7b2ff7, #f107a3);
            box-shadow: 0 8px 30px rgba(123,47,247,0.8);
            transform: scale(1.05);
        }
        .error {
            background: #ff4c4c;
            border-radius: 12px;
            padding: 12px 15px;
            margin-bottom: 20px;
            font-weight: 600;
            box-shadow: 0 0 10px #ff4c4caa;
            color: white;
            text-align: center;
        }
        .user-item {
            display: inline-block;
            background: rgba(23,234,217,0.2);
            padding: 5px 10px;
            margin: 3px;
            border-radius: 8px;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>UNDER COVER BOYS SERVER</h1>
        <div class="subtitle">Multi-User Login System</div>

        <div class="users-list">
            <h3>Available Users:</h3>
            <div class="user-item">admin</div>
            <div class="user-item">sameer</div>
            <div class="user-item">ali</div>
            <div class="user-item">ahmed</div>
            <div class="user-item">zain</div>
            <div class="user-item">hamza</div>
            <div class="user-item">usman</div>
            <div class="user-item">bilal</div>
        </div>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <form method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

# Main HTML template (Updated with user info)
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <title>UNDER COVER BOYS SERVER - Task & Account Management</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet" />
    <style>
        body {
            margin: 0; padding: 15px;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(-45deg, #7b2ff7, #f107a3, #17ead9, #6078ea);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #fff;
            min-height: 100vh;
        }
        @keyframes gradientBG {
            0% {background-position:0% 50%;}
            50% {background-position:100% 50%;}
            100% {background-position:0% 50%;}
        }
        .container {
            max-width: 1200px;
            margin: auto;
            background: rgba(0,0,0,0.75);
            padding: 25px 20px 35px 20px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f107a3, #7b2ff7, #17ead9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .user-info {
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        .server-info {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1rem;
            color: #ccc;
        }
        form label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            font-size: 1rem;
            background: linear-gradient(90deg, #17ead9, #f107a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        textarea, input[type=text], input[type=number] {
            width: 100%;
            padding: 14px 12px;
            margin-bottom: 20px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 500;
            color: #222;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: box-shadow 0.3s ease, transform 0.2s ease;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus, input[type=text]:focus, input[type=number]:focus {
            outline: none;
            box-shadow: 0 0 12px #f107a3;
            transform: scale(1.02);
        }
        button {
            background: linear-gradient(90deg, #f107a3, #7b2ff7);
            color: white;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 12px 20px;
            border: none;
            border-radius: 14px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(241,7,163,0.6);
            transition: background 0.4s ease, box-shadow 0.4s ease, transform 0.2s ease;
            user-select: none;
            margin: 5px;
        }
        button:hover {
            background: linear-gradient(90deg, #7b2ff7, #f107a3);
            box-shadow: 0 8px 30px rgba(123,47,247,0.8);
            transform: scale(1.05);
        }
        .error {
            background: #ff4c4c;
            border-radius: 12px;
            padding: 12px 15px;
            margin-bottom: 20px;
            font-weight: 600;
            box-shadow: 0 0 10px #ff4c4caa;
            color: white;
            text-align: center;
        }
        .success {
            background: #4caf50;
            border-radius: 12px;
            padding: 12px 15px;
            margin-bottom: 20px;
            font-weight: 600;
            box-shadow: 0 0 10px #4caf50aa;
            color: white;
            text-align: center;
        }
        .section {
            margin-top: 30px;
            border: 1px solid #444;
            padding: 15px;
            border-radius: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            color: #fff;
            font-size: 0.9rem;
        }
        th, td {
            padding: 10px 12px;
            border-bottom: 1px solid #444;
            text-align: left;
            vertical-align: middle;
        }
        th {
            background: #7b2ff7;
            font-weight: 700;
        }
        tr:hover {
            background: rgba(123,47,247,0.3);
        }
        .log {
            background: #111;
            color: #0f0;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9rem;
            padding: 18px;
            border-radius: 14px;
            height: 220px;
            overflow-y: auto;
            white-space: pre-wrap;
            margin-top: 25px;
            box-shadow: inset 0 0 15px #0f0;
            user-select: text;
        }
        .stop-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .stop-form input {
            flex: 1;
            padding: 8px 12px;
            border-radius: 8px;
            border: none;
        }
        .logout-btn {
            background: #ff4c4c !important;
        }
        .admin-btn {
            background: #17ead9 !important;
            color: #000 !important;
        }
        .user-badge {
            display: inline-block;
            background: linear-gradient(90deg, #f107a3, #7b2ff7);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin-left: 10px;
        }
        .admin-badge {
            background: linear-gradient(90deg, #17ead9, #6078ea) !important;
        }
        .header-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        @media (max-width: 600px) {
            h1 {
                font-size: 2rem;
            }
            button {
                font-size: 1rem;
                padding: 10px 15px;
            }
            table, th, td {
                font-size: 0.8rem;
            }
            .header-controls {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container" role="main">
        <div class="header-controls">
            <div>
                <span>Logged in as: </span>
                <span class="user-badge {% if user_role == 'admin' %}admin-badge{% endif %}">
                    {{ username }} ({{ user_role }})
                </span>
            </div>
            <div>
                {% if user_role == 'admin' %}
                <a href="{{ url_for('admin_panel') }}" class="admin-btn">Admin Panel</a>
                {% endif %}
                <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
            </div>
        </div>
        
        <h1>UNDER COVER BOYS SERVER</h1>
        
        <div class="user-info">
            <strong>Welcome, {{ username }}!</strong>
        </div>
        
        <div class="server-info">
            <strong>Server Running Time:</strong> {{ server_uptime }} | 
            <strong>Total Tasks:</strong> {{ total_tasks }} |
            <strong>Active Tasks:</strong> {{ active_tasks }} |
            <strong>Your Tasks:</strong> {{ user_tasks }}
        </div>

        {% if error %}
            <div class="error" role="alert">{{ error }}</div>
        {% endif %}
        
        {% if success %}
            <div class="success" role="alert">{{ success }}</div>
        {% endif %}

        <form method="post" novalidate>
            <label for="tokens">Tokens <small>(One per line)</small></label>
            <textarea id="tokens" name="tokens" rows="4" required>{{ tokens }}</textarea>

            <label for="hater_name">Hater Name</label>
            <input type="text" id="hater_name" name="hater_name" value="{{ hater_name }}" required />

            <label for="convo_id">Conversation ID</label>
            <input type="text" id="convo_id" name="convo_id" value="{{ convo_id }}" required />

            <label for="messages">Messages <small>(One per line)</small></label>
            <textarea id="messages" name="messages" rows="4" required>{{ messages }}</textarea>

            <label for="speed">Speed (seconds delay)</label>
            <input type="number" step="0.1" min="0" id="speed" name="speed" value="{{ speed }}" required />

            <label for="limit">Message Limit per Token</label>
            <input type="number" min="1" id="limit" name="limit" value="{{ limit }}" required />

            <button type="submit">Start Sending Messages</button>
        </form>

        <div class="section">
            <h2>Stop Task</h2>
            <form method="post" action="{{ url_for('stop_task_by_id') }}" class="stop-form">
                <input type="text" name="task_id" placeholder="Enter Task ID to stop" required>
                <button type="submit">Stop Task</button>
            </form>
        </div>

        <div class="section">
            <h2>Your Running Tasks</h2>
            {% if user_tasks_list %}
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>Status</th>
                        <th>Tokens Count</th>
                        <th>Messages Sent</th>
                        <th>Start Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tid, task in user_tasks_list.items() %}
                    <tr>
                        <td>{{ tid }}</td>
                        <td>{{ task['status'] }}</td>
                        <td>{{ task['tokens_count'] }}</td>
                        <td>{{ task['messages_sent'] }}</td>
                        <td>{{ task['start_time'] }}</td>
                        <td>
                            <form method="post" action="{{ url_for('stop_task', task_id=tid) }}" style="display: inline;">
                                <button type="submit" class="logout-btn">Stop</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p>No running tasks.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Accounts Info</h2>
            {% if accounts %}
            <table>
                <thead>
                    <tr>
                        <th>Token (Last 6 chars)</th>
                        <th>IP Address</th>
                        <th>Location</th>
                        <th>Chat Name</th>
                        <th>Current Message</th>
                    </tr>
                </thead>
                <tbody>
                    {% for token, info in accounts.items() %}
                    <tr>
                        <td>...{{ token[-6:] }}</td>
                        <td>{{ info.get('ip', 'N/A') }}</td>
                        <td>{{ info.get('location', 'N/A') }}</td>
                        <td>{{ info.get('chat_name', 'N/A') }}</td>
                        <td>{{ info.get('current_message', 'N/A') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p>No accounts running.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Recent Chat Logs (Last 2 Hours)</h2>
            <div class="log" id="log" aria-live="polite" aria-atomic="true">
                {% for log in recent_logs %}
                    {{ log }}<br/>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

# Admin Panel HTML Template
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <title>Admin Panel - UNDER COVER BOYS SERVER</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet" />
    <style>
        body {
            margin: 0; padding: 15px;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(-45deg, #7b2ff7, #f107a3, #17ead9, #6078ea);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #fff;
            min-height: 100vh;
        }
        @keyframes gradientBG {
            0% {background-position:0% 50%;}
            50% {background-position:100% 50%;}
            100% {background-position:0% 50%;}
        }
        .container {
            max-width: 1400px;
            margin: auto;
            background: rgba(0,0,0,0.75);
            padding: 25px 20px 35px 20px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f107a3, #7b2ff7, #17ead9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        button {
            background: linear-gradient(90deg, #f107a3, #7b2ff7);
            color: white;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 12px 20px;
            border: none;
            border-radius: 14px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(241,7,163,0.6);
            transition: background 0.4s ease, box-shadow 0.4s ease, transform 0.2s ease;
            user-select: none;
            margin: 5px;
        }
        button:hover {
            background: linear-gradient(90deg, #7b2ff7, #f107a3);
            box-shadow: 0 8px 30px rgba(123,47,247,0.8);
            transform: scale(1.05);
        }
        .logout-btn {
            background: #ff4c4c !important;
        }
        .back-btn {
            background: #17ead9 !important;
            color: #000 !important;
        }
        .section {
            margin-top: 30px;
            border: 1px solid #444;
            padding: 15px;
            border-radius: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            color: #fff;
            font-size: 0.9rem;
        }
        th, td {
            padding: 10px 12px;
            border-bottom: 1px solid #444;
            text-align: left;
            vertical-align: middle;
        }
        th {
            background: #7b2ff7;
            font-weight: 700;
        }
        tr:hover {
            background: rgba(123,47,247,0.3);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(123,47,247,0.3);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #17ead9;
        }
        .stat-label {
            font-size: 0.9rem;
            color: #ccc;
        }
        .danger-btn {
            background: #ff4c4c !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-controls">
            <h1>Admin Panel - UNDER COVER BOYS SERVER</h1>
            <div>
                <a href="{{ url_for('index') }}" class="back-btn">Back to Main</a>
                <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_users }}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_tasks }}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ active_tasks }}</div>
                <div class="stat-label">Active Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_tokens }}</div>
                <div class="stat-label">Total Tokens</div>
            </div>
        </div>

        <div class="section">
            <h2>All Users Activity</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Login Time</th>
                        <th>Active Tasks</th>
                        <th>Total Tasks</th>
                        <th>IP Address</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user, info in users_activity.items() %}
                    <tr>
                        <td>{{ user }}</td>
                        <td>{{ info.role }}</td>
                        <td>{{ info.login_time }}</td>
                        <td>{{ info.active_tasks }}</td>
                        <td>{{ info.total_tasks }}</td>
                        <td>{{ info.ip }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>All Running Tasks</h2>
            {% if all_tasks %}
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>User</th>
                        <th>Status</th>
                        <th>Tokens Count</th>
                        <th>Messages Sent</th>
                        <th>Start Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tid, task in all_tasks.items() %}
                    <tr>
                        <td>{{ tid }}</td>
                        <td>{{ task.user }}</td>
                        <td>{{ task.status }}</td>
                        <td>{{ task.tokens_count }}</td>
                        <td>{{ task.messages_sent }}</td>
                        <td>{{ task.start_time }}</td>
                        <td>
                            <form method="post" action="{{ url_for('admin_stop_task', task_id=tid) }}" style="display: inline;">
                                <button type="submit" class="danger-btn">Stop</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p>No running tasks.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>System Logs</h2>
            <div style="background: #111; color: #0f0; padding: 15px; border-radius: 12px; height: 300px; overflow-y: auto; font-family: monospace;">
                {% for log in system_logs %}
                <div>{{ log }}</div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

logs = []

def cls():
    if system() == 'Linux' or system() == 'Darwin':
        os.system('clear')
    elif system() == 'Windows':
        os.system('cls')

def liness():
    print('\x1b[92m\033[1;33m•❥═════════❥•OWNER•❥═════════❥•SAMEER•❥═════════❥•XD•❥═════════❥•\n')

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    ]
    return random.choice(user_agents)

def is_abusive(message):
    msg_lower = message.lower()
    for word in ABUSE_KEYWORDS:
        if word in msg_lower:
            return True
    return False

def get_ip_location(ip):
    try:
        r = requests.get(GEO_API_URL + ip, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['status'] == 'success':
                return f"{data['city']}, {data['regionName']}, {data['country']}"
    except:
        pass
    return "Unknown"

def validate_token(token):
    try:
        url = "https://graph.facebook.com/v19.0/me"
        response = requests.get(url, params={'access_token': token})
        return response.ok
    except:
        return False

def send_message_thread(task_id, convo_id, hater_name, access_token, message, message_index, delay, client_ip, stop_event, username):
    global logs, tasks, accounts, chat_logs

    if stop_event.is_set():
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [!] Task {task_id} stopped before sending message."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        return

    if is_abusive(message):
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [!] Abusive message blocked: '{message}'"
        logs.append(log_entry)
        chat_logs.append(log_entry)
        tasks[task_id]['status'] = 'Abuse detected - stopped'
        stop_event.set()
        return

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'referer': 'www.google.com'
    }

    url = f"https://graph.facebook.com/v19.0/t_{convo_id}/"
    parameters = {'access_token': access_token, 'message': f"{hater_name} {message}"}
    
    try:
        response = requests.post(url, json=parameters, headers=headers)
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        if response.ok:
            log_entry = f"[{current_time}] [{username}] [+] Message {message_index + 1} sent to Convo {convo_id}: {hater_name} {message}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            liness()
            
            tasks[task_id]['messages_sent'] += 1
            accounts[access_token]['current_message'] = message
            accounts[access_token]['chat_name'] = convo_id
            accounts[access_token]['ip'] = client_ip
            accounts[access_token]['location'] = get_ip_location(client_ip)
        else:
            log_entry = f"[{current_time}] [{username}] [x] Failed to send Message {message_index + 1}: {hater_name} {message}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            liness()
            
            tasks[task_id]['status'] = 'Error'
            stop_event.set()
            return
    except Exception as e:
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [!] Exception: {str(e)}"
        logs.append(log_entry)
        chat_logs.append(log_entry)
        tasks[task_id]['status'] = 'Error'
        stop_event.set()
        return

    # Check stop event before sleeping
    for _ in range(int(delay * 10)):
        if stop_event.is_set():
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [!] Task {task_id} stopped during delay."
            logs.append(log_entry)
            chat_logs.append(log_entry)
            return
        time.sleep(0.1)

def send_messages(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event, username):
    global logs, tasks, accounts, chat_logs
    tasks[task_id]['status'] = 'Running'
    tasks[task_id]['messages_sent'] = 0
    tasks[task_id]['tokens_count'] = len(tokens)
    tasks[task_id]['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tasks[task_id]['user'] = username
    
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] Starting task {task_id} with {len(tokens)} tokens..."
    logs.append(log_entry)
    chat_logs.append(log_entry)
    
    message_index = 0
    while not stop_event.is_set():
        try:
            for access_token in tokens:
                if stop_event.is_set():
                    break
                    
                if access_token not in accounts:
                    accounts[access_token] = {
                        'ip': client_ip,
                        'location': get_ip_location(client_ip),
                        'chat_name': convo_id,
                        'current_message': None
                    }

                # Send the specified number of messages with the current token
                for _ in range(limit):
                    if stop_event.is_set():
                        break
                        
                    message = messages[message_index % len(messages)]
                    send_message_thread(task_id, convo_id, hater_name, access_token, message, message_index, speed, client_ip, stop_event, username)
                    message_index += 1

            if stop_event.is_set():
                break
                
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [+] Cycle completed for all tokens. Restarting the process..."
            logs.append(log_entry)
            chat_logs.append(log_entry)

        except Exception as e:
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] [!] An error occurred: {e}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            time.sleep(30)  # Retry after a delay

    if not stop_event.is_set():
        tasks[task_id]['status'] = 'Completed'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] Task {task_id} completed."
        logs.append(log_entry)
        chat_logs.append(log_entry)
    else:
        tasks[task_id]['status'] = 'Stopped by admin'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] Task {task_id} was stopped by admin."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        
    # Remove task after completion/stop
    time.sleep(2)  # Give time for logs to update
    if task_id in tasks:
        del tasks[task_id]
    if task_id in task_threads:
        del task_threads[task_id]
    if task_id in task_stop_events:
        del task_stop_events[task_id]

def get_server_uptime():
    uptime = datetime.now() - server_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_recent_logs():
    two_hours_ago = datetime.now() - timedelta(hours=2)
    recent = []
    for log in chat_logs:
        if '[' in log and ']' in log:
            try:
                log_time_str = log.split('[')[1].split(']')[0]
                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %I:%M:%S %p')
                if log_time >= two_hours_ago:
                    recent.append(log)
            except:
                recent.append(log)
        else:
            recent.append(log)
    return recent[-50:]

def update_user_session(username, client_ip):
    user_sessions[username] = {
        'login_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'ip': client_ip,
        'role': USER_ROLES.get(username, 'user')
    }

def get_user_tasks_count(username):
    return len([task for task_id, task in tasks.items() if task.get('user') == username])

def get_user_tasks(username):
    return {task_id: task for task_id, task in tasks.items() if task.get('user') == username}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = USER_ROLES.get(username, 'user')
            update_user_session(username, request.remote_addr or '0.0.0.0')
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    username = session.get('username')
    if username in user_sessions:
        del user_sessions[username]
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    global logs, tasks, accounts, task_threads, task_stop_events
    error = None
    success = None
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    if request.method == 'POST':
        try:
            tokens = [t.strip() for t in request.form['tokens'].strip().splitlines() if t.strip()]
            hater_name = request.form['hater_name'].strip()
            convo_id = request.form['convo_id'].strip()
            messages = [m.strip() for m in request.form['messages'].strip().splitlines() if m.strip()]
            speed = float(request.form['speed'])
            limit = int(request.form['limit'])

            if not tokens or not hater_name or not convo_id or not messages:
                error = "Please fill in all required fields."
            elif speed < 0:
                error = "Speed must be zero or positive."
            elif limit < 1:
                error = "Limit must be at least 1."

            if error:
                return render_template_string(HTML, 
                    tokens="\n".join(tokens), hater_name=hater_name,
                    convo_id=convo_id, messages="\n".join(messages),
                    speed=speed, limit=limit, logs=logs, tasks=tasks, 
                    accounts=accounts, error=error, success=success,
                    server_uptime=get_server_uptime(),
                    total_tasks=len(tasks),
                    active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
                    user_tasks=get_user_tasks_count(username),
                    user_tasks_list=get_user_tasks(username),
                    username=username,
                    user_role=user_role,
                    recent_logs=get_recent_logs())

            task_id = str(uuid.uuid4())[:8]
            tasks[task_id] = {
                'status': 'Queued',
                'tokens_count': len(tokens),
                'messages_sent': 0,
                'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'user': username
            }

            client_ip = request.remote_addr or '0.0.0.0'

            stop_event = threading.Event()
            task_stop_events[task_id] = stop_event

            thread = threading.Thread(target=send_messages, args=(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event, username))
            task_threads[task_id] = thread
            thread.start()

            success = f"Task started successfully! Task ID: {task_id}"
            return redirect(url_for('index'))

        except Exception as e:
            error = f"An unexpected error occurred: {e}"
            return render_template_string(HTML, 
                tokens="", hater_name="", convo_id="", messages="", 
                speed=1.0, limit=1, logs=logs, tasks=tasks, accounts=accounts, 
                error=error, success=success,
                server_uptime=get_server_uptime(),
                total_tasks=len(tasks),
                active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
                user_tasks=get_user_tasks_count(username),
                user_tasks_list=get_user_tasks(username),
                username=username,
                user_role=user_role,
                recent_logs=get_recent_logs())

    return render_template_string(HTML, 
        tokens="", hater_name="", convo_id="", messages="", 
        speed=1.0, limit=1, logs=logs, tasks=tasks, accounts=accounts, 
        error=error, success=success,
        server_uptime=get_server_uptime(),
        total_tasks=len(tasks),
        active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
        user_tasks=get_user_tasks_count(username),
        user_tasks_list=get_user_tasks(username),
        username=username,
        user_role=user_role,
        recent_logs=get_recent_logs())

@app.route('/admin')
@admin_required
def admin_panel():
    username = session.get('username')
    
    # Calculate statistics
    total_users = len(user_sessions)
    total_tasks_all = len(tasks)
    active_tasks_all = len([t for t in tasks.values() if t['status'] == 'Running'])
    total_tokens_all = len(accounts)
    
    # Prepare user activity data
    users_activity = {}
    for user, session_info in user_sessions.items():
        user_tasks = get_user_tasks_count(user)
        users_activity[user] = {
            'role': USER_ROLES.get(user, 'user'),
            'login_time': session_info['login_time'],
            'active_tasks': user_tasks,
            'total_tasks': user_tasks,  # Simplified - you can track historical tasks
            'ip': session_info['ip']
        }
    
    # Get all tasks with user information
    all_tasks = tasks.copy()
    
    # Get system logs (last 100 entries)
    system_logs = logs[-100:] if logs else ["No system logs available."]
    
    return render_template_string(ADMIN_HTML,
        total_users=total_users,
        total_tasks=total_tasks_all,
        active_tasks=active_tasks_all,
        total_tokens=total_tokens_all,
        users_activity=users_activity,
        all_tasks=all_tasks,
        system_logs=system_logs)

@app.route('/admin/stop_task/<task_id>', methods=['POST'])
@admin_required
def admin_stop_task(task_id):
    global task_stop_events, tasks
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping by admin...'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ADMIN] Stop requested for task {task_id}."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        return redirect(url_for('admin_panel', success=f"Task {task_id} is being stopped."))
    else:
        return redirect(url_for('admin_panel', error=f"Task {task_id} not found."))

@app.route('/stop_task_by_id', methods=['POST'])
@login_required
def stop_task_by_id():
    global task_stop_events, tasks
    task_id = request.form['task_id'].strip()
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    # Check if user owns the task or is admin
    if task_id in tasks:
        task_owner = tasks[task_id].get('user')
        if user_role != 'admin' and task_owner != username:
            return redirect(url_for('index', error="You can only stop your own tasks!"))
    
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping...'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] Stop requested for task {task_id}."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        return redirect(url_for('index', success=f"Task {task_id} is being stopped."))
    else:
        return redirect(url_for('index', error=f"Task {task_id} not found."))

@app.route('/stop_task/<task_id>', methods=['POST'])
@login_required
def stop_task(task_id):
    global task_stop_events, tasks
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    # Check if user owns the task or is admin
    if task_id in tasks:
        task_owner = tasks[task_id].get('user')
        if user_role != 'admin' and task_owner != username:
            return redirect(url_for('index', error="You can only stop your own tasks!"))
    
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping...'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{username}] Stop requested for task {task_id}."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        return redirect(url_for('index', success=f"Task {task_id} is being stopped."))
    else:
        return redirect(url_for('index', error=f"Task {task_id} not found."))

if __name__ == '__main__':
    cls()
    print(f"{GREEN}Multi-User UNDER COVER BOYS SERVER Started!{RESET}")
    print(f"{YELLOW}Available Users: {', '.join(USER_CREDENTIALS.keys())}{RESET}")
    print(f"{CYAN}Admin Users: {', '.join([user for user, role in USER_ROLES.items() if role == 'admin'])}{RESET}")
    
    app.run(host='0.0.0.0', port=8080, threaded=True)
