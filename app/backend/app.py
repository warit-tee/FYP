from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Flask backend is running"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "ok"
    })