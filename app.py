from flask import Flask, render_template

app = Flask(__name__)

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


import os
port = int(os.environ.get("PORT", 10000))
app.run(host='0.0.0.0', port=port)