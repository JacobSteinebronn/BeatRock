from flask import Flask, request, jsonify
import uuid
import requests
import json
import time

proxy_uuid = str(uuid.uuid4())

def get_host():
    try:
        with open("orchestrator_host.txt") as file:
            return file.readlines()[0].strip()
    except:
        fetch_response = requests.get("https://raw.githubusercontent.com/JacobSteinebronn/BeatRock/main/orchestrator_host.txt")
        return fetch_response._content.decode("utf-8").strip()


def update_orchestrator():
    orchestrator_url = f'http://{get_host()}/register'

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
    app.run(port=8080, host="0.0.0.0")