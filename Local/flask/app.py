from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os, requests
from urllib.parse import urlparse
from datetime import datetime

CONFIG_FOLDER = 'configs'
CONFIG_FILE = 'settings.json'
CONFIG_PATH = os.path.join(CONFIG_FOLDER, CONFIG_FILE)

DEFAULT_CONFIG = {
    "refresh_interval": 30,  # 默认刷新间隔为 30 分钟
    "ip_source_url": "http://api.ipify.org"  # 默认的 IP 查询源 URL
}
def read_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, 'r') as file:
        config = json.load(file)
        for key in DEFAULT_CONFIG:
            config.setdefault(key, DEFAULT_CONFIG[key])
        return config


def write_config(data):
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    with open(CONFIG_PATH, 'w') as file:
        json.dump(data, file, indent=4)


app = Flask(__name__)

@app.route('/')
def index():
    config = read_config()
    return render_template('index.html', config=config)

@app.route('/ip-lookup-setting')
def ip_lookup_setting():
    config = read_config()
    return render_template('ip_lookup_setting.html', config=config)

@app.route('/update-ip-lookup-setting', methods=['POST'])
def update_ip_lookup_setting():
    refresh_interval = request.form['refreshInterval']
    ip_source_url = "http://api.ipify.org"  # 默认 URL

    if request.form.get('ipSource') == 'custom':
        custom_ip_source_url = request.form['customIpSourceUrl']
        if is_valid_url(custom_ip_source_url):
            ip_source_url = custom_ip_source_url

    new_config = {
        "refresh_interval": int(refresh_interval),
        "ip_source_url": ip_source_url
    }
    write_config(new_config)

    return redirect(url_for('index'))

@app.route('/get-current-ip')
def get_current_ip():
    config = read_config()
    ip_source_url = config['ip_source_url']
    try:
        response = requests.get(ip_source_url)
        current_ip = response.text
    except requests.RequestException as e:
        current_ip = "Error: " + str(e)
    return jsonify({'current_ip': current_ip})

def record_ip_change(current_ip):
    # 读取现有的历史记录
    if os.path.exists('logs/ip_logs.json'):
        with open('logs/ip_logs.json', 'r') as file:
            history = json.load(file)
    else:
        history = []

    # 添加新记录
    history.append({'ip': current_ip, 'timestamp': datetime.now().isoformat()})
    with open('logs/ip_logs.json', 'w') as file:
        json.dump(history, file, indent=4)

@app.route('/ip-history')
def ip_history():
    if os.path.exists('logs/ip_logs.json'):
        with open('logs/ip_logs.json', 'r') as file:
            history = json.load(file)
    else:
        history = []
    return render_template('ip_history.html', history=history)

# ------------- HELPER FUNCTIONS -------------
# --------------------------------------------
    
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

if __name__ == '__main__':
    app.run(debug=True)

