import requests
import json
import uuid

chain = ["rock", "paper", "fire", "water", "sponge", "lava", "ice"]

def beats(a, b, uid):
    url = "https://www.whatbeatsrock.com/api/vs"
    headers = {
        "User-Agent": "@meaf, on discord",
    }
    data = {"prev":a,"guess":b,"gid":uid}

    response = requests.post(url, headers=headers, json=data)
    code = response.status_code
    if code == 200:
        resp = json.loads(response._content.decode('utf-8'))["data"]
        return resp["guess_wins"]
    raise Exception(f"{response.__dict__}\n\nError {code}: \n{response._content.decode('utf-8')}")

while True:
    try:
        uid = str(uuid.uuid1())
        for i in range(1, len(chain)):
            print(beats(chain[i-1], chain[i], uid))
    except Exception as e:
        print(e)
        input()
        raise e
# uid = "dda5eb32-43e0-4fb3-b03a-91377cf515b7"

# print(beats("rock", "paper"))
# print(beats("paper", "papers"))

# url = "https://www.whatbeatsrock.com/api/scores"
# headers = {
#     "User-Agent": "Jacob's Script",
# }
# "🅰 🅱 🅲 🅳 🅴 🅵 🅶 🅷 🅸 🅹 🅺 🅻 🅼 🅽 🅾 🅿 🆀 🆁 🆂 🆃 🆄 🆅 🆆 🆇 🆈 🆉"
# "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿"
# data = {"initials":"JAS","score":1,"gid":uid, "text": "papers 🅷🅴🅻🅻🅾 did not beat paper 🤜"}

# response = requests.post(url, headers=headers, json=data)
# print(response.__dict__)

