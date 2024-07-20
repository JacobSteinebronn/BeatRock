from flask import Flask, request, jsonify
import uuid
import requests
import json
import asyncio

app = Flask(__name__)

port = 5001

@app.route('/register', methods=['POST'])
def post_handler():
    data = request.get_json()
    print(data)
    return jsonify({}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)