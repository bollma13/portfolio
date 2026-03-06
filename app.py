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

if __name__ == '__main__':
    # debug=True enables the "Hot Reload" feature
    app.run(debug=True)