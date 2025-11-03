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
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key

# Login credentials
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "5550561"

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

# Login HTML template
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
            max-width: 400px;
            width: 100%;
            background: rgba(0,0,0,0.75);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            font-weight: 700;
            font-size: 2rem;
            margin-bottom: 30px;
            background: linear-gradient(90deg, #f107a3, #7b2ff7, #17ead9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
    </style>
</head>
<body>
    <div class="login-container">
        <h1>UNDER COVER BOYS SERVER</h1>
        <h2 style="text-align: center; margin-bottom: 30px;">Login Required</h2>

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

# Main HTML template (updated)
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
        .server-info {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.1rem;
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
            position: absolute;
            top: 20px;
            right: 20px;
            background: #ff4c4c !important;
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
            .logout-btn {
                position: relative;
                top: 0;
                right: 0;
                margin-bottom: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container" role="main">
        <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
        <h1>UNDER COVER BOYS SERVER</h1>
        
        <div class="server-info">
            <strong>Server Running Time:</strong> {{ server_uptime }} | 
            <strong>Total Tasks:</strong> {{ total_tasks }} |
            <strong>Active Tasks:</strong> {{ active_tasks }}
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
            <h2>Running Tasks</h2>
            {% if tasks %}
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>Status</th>
                        <th>Tokens Count</th>
                        <th>Messages Sent</th>
                        <th>Start Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tid, task in tasks.items() %}
                    <tr>
                        <td>{{ tid }}</td>
                        <td>{{ task['status'] }}</td>
                        <td>{{ task['tokens_count'] }}</td>
                        <td>{{ task['messages_sent'] }}</td>
                        <td>{{ task['start_time'] }}</td>
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

def send_message_thread(task_id, convo_id, hater_name, access_token, message, message_index, delay, client_ip, stop_event):
    global logs, tasks, accounts, chat_logs

    if stop_event.is_set():
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Task {task_id} stopped before sending message."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        return

    if is_abusive(message):
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Abusive message blocked: '{message}'"
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
            log_entry = f"[{current_time}] [+] Message {message_index + 1} sent to Convo {convo_id}: {hater_name} {message}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            liness()
            
            tasks[task_id]['messages_sent'] += 1
            accounts[access_token]['current_message'] = message
            accounts[access_token]['chat_name'] = convo_id
            accounts[access_token]['ip'] = client_ip
            accounts[access_token]['location'] = get_ip_location(client_ip)
        else:
            log_entry = f"[{current_time}] [x] Failed to send Message {message_index + 1}: {hater_name} {message}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            liness()
            
            tasks[task_id]['status'] = 'Error'
            stop_event.set()
            return
    except Exception as e:
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Exception: {str(e)}"
        logs.append(log_entry)
        chat_logs.append(log_entry)
        tasks[task_id]['status'] = 'Error'
        stop_event.set()
        return

    # Check stop event before sleeping
    for _ in range(int(delay * 10)):
        if stop_event.is_set():
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Task {task_id} stopped during delay."
            logs.append(log_entry)
            chat_logs.append(log_entry)
            return
        time.sleep(0.1)

def send_messages(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event):
    global logs, tasks, accounts, chat_logs
    tasks[task_id]['status'] = 'Running'
    tasks[task_id]['messages_sent'] = 0
    tasks[task_id]['tokens_count'] = len(tokens)
    tasks[task_id]['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting task {task_id} with {len(tokens)} tokens..."
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
                    send_message_thread(task_id, convo_id, hater_name, access_token, message, message_index, speed, client_ip, stop_event)
                    message_index += 1

            if stop_event.is_set():
                break
                
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [+] Cycle completed for all tokens. Restarting the process..."
            logs.append(log_entry)
            chat_logs.append(log_entry)

        except Exception as e:
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] An error occurred: {e}"
            logs.append(log_entry)
            chat_logs.append(log_entry)
            time.sleep(30)  # Retry after a delay

    if not stop_event.is_set():
        tasks[task_id]['status'] = 'Completed'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task {task_id} completed."
        logs.append(log_entry)
        chat_logs.append(log_entry)
    else:
        tasks[task_id]['status'] = 'Stopped by admin'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task {task_id} was stopped by admin."
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
        # Extract timestamp from log entry if available
        if '[' in log and ']' in log:
            try:
                log_time_str = log.split('[')[1].split(']')[0]
                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %I:%M:%S %p')
                if log_time >= two_hours_ago:
                    recent.append(log)
            except:
                recent.append(log)  # If timestamp parsing fails, include it anyway
        else:
            recent.append(log)  # If no timestamp, include it
    return recent[-50:]  # Return last 50 entries to avoid overload

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    global logs, tasks, accounts, task_threads, task_stop_events
    error = None
    success = None
    
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
                return render_template_string(HTML, tokens="\n".join(tokens), hater_name=hater_name,
                                            convo_id=convo_id, messages="\n".join(messages),
                                            speed=speed, limit=limit, logs=logs, tasks=tasks, 
                                            accounts=accounts, error=error, success=success,
                                            server_uptime=get_server_uptime(),
                                            total_tasks=len(tasks),
                                            active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
                                            recent_logs=get_recent_logs())

            task_id = str(uuid.uuid4())[:8]
            tasks[task_id] = {
                'status': 'Queued',
                'tokens_count': len(tokens),
                'messages_sent': 0,
                'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            client_ip = request.remote_addr or '0.0.0.0'

            stop_event = threading.Event()
            task_stop_events[task_id] = stop_event

            thread = threading.Thread(target=send_messages, args=(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event))
            task_threads[task_id] = thread
            thread.start()

            success = f"Task started successfully! Task ID: {task_id}"
            return redirect(url_for('index'))

        except Exception as e:
            error = f"An unexpected error occurred: {e}"
            return render_template_string(HTML, tokens="", hater_name="", convo_id="", messages="", 
                                        speed=1.0, limit=1, logs=logs, tasks=tasks, accounts=accounts, 
                                        error=error, success=success,
                                        server_uptime=get_server_uptime(),
                                        total_tasks=len(tasks),
                                        active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
                                        recent_logs=get_recent_logs())

    return render_template_string(HTML, tokens="", hater_name="", convo_id="", messages="", 
                                speed=1.0, limit=1, logs=logs, tasks=tasks, accounts=accounts, 
                                error=error, success=success,
                                server_uptime=get_server_uptime(),
                                total_tasks=len(tasks),
                                active_tasks=len([t for t in tasks.values() if t['status'] == 'Running']),
                                recent_logs=get_recent_logs())

@app.route('/stop_task_by_id', methods=['POST'])
@login_required
def stop_task_by_id():
    global task_stop_events, tasks
    task_id = request.form['task_id'].strip()
    
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping...'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Stop requested for task {task_id} by admin."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        
        # Task will be automatically removed in send_messages function
        return redirect(url_for('index', success=f"Task {task_id} is being stopped."))
    else:
        return redirect(url_for('index', error=f"Task {task_id} not found."))

@app.route('/stop_task/<task_id>', methods=['POST'])
@login_required
def stop_task(task_id):
    global task_stop_events, tasks
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping...'
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [!] Stop requested for task {task_id} by admin."
        logs.append(log_entry)
        chat_logs.append(log_entry)
        
        # Task will be automatically removed in send_messages function
        return redirect(url_for('index', success=f"Task {task_id} is being stopped."))
    else:
        return redirect(url_for('index', error=f"Task {task_id} not found."))

if __name__ == '__main__':
    cls()
    app.run(host='0.0.0.0', port=8080, threaded=True)