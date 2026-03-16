from flask import Flask, render_template
import os
import json

app = Flask(__name__)

# --- Public Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/personal')
def personal():
    return render_template('personal.html')

@app.route('/personal/photography')
def photography_gallery():
    return render_template('photography.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

# --- Hidden Bridge Route ---
# @app.route('/bridge')
# def hidden_bridge_page():
#     file_path = os.path.join(app.static_folder, 'bridge_status.json')
    
#     try:
#         with open(file_path, 'r') as f:
#             bridge_data = json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         bridge_data = {}

#     # SAFETY DEFAULTS: Prevents the "UndefinedError: metrics" crash
#     if 'metrics' not in bridge_data:
#         bridge_data['metrics'] = {"pct_open": 100, "pct_closed": 0}
#     if 'history' not in bridge_data:
#         bridge_data['history'] = []
#     if 'current_status' not in bridge_data:
#         # Check for 'status' (old key) or default to UNKNOWN
#         bridge_data['current_status'] = bridge_data.get('status', 'UNKNOWN')
#     if 'last_update' not in bridge_data:
#         bridge_data['last_update'] = bridge_data.get('time', 'N/A')

#     return render_template('bridge.html', data=bridge_data)

# --- Server Start (Always last) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)