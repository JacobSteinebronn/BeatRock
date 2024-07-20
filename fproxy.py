from flask import Flask, request, jsonify
import uuid
import requests
import json
import asyncio
import time

orchestrator_url = 'http://127.0.0.1:5001/register'
proxy_uuid = str(uuid.uuid4())

def update_orchestrator():
    while True:
        try:
            rsp = requests.post(orchestrator_url, json={"proxy_uuid": proxy_uuid})
            if rsp.status_code == 200:
                return
        except requests.ConnectionError:
            pass

        print("Failed to connect to orchestrator!")
        time.sleep(60)

app = Flask(__name__)

@app.route('/<path:path>', methods=['POST'])
def post_handler(path):
    data = request.get_json()
    upstream_url = (f"https://www.whatbeatsrock.com/{path}").strip()
    headers = {"User-Agent": "@meaf, on discord"}

    upstream_response = requests.post(upstream_url, json=data, headers=headers)
    
    response_body = json.loads(upstream_response._content.decode("utf-8"))
    response_body["proxy_uuid"] = proxy_uuid
    
    return jsonify(response_body), upstream_response.status_code

if __name__ == '__main__':
    update_orchestrator()
    app.run(debug=True)