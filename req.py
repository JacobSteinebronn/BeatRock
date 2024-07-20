import requests
import json
import uuid

class God:
    def __init__(self, name, targ):
        self.name = name
        self.targ = targ
    
    def __str__(self):
        if self.targ == "__NOTHING": return f"A person named {self.name} who breaks rocks"
        return f"A person named {self.name} who is stronger, smarter, and faster than {self.targ}"

    def to_json(self): return {"name": self.name, "targ": self.targ}
    def to_compact(str): return f"{self.name}>{self.targ}"

global_uid = str(uuid.uuid1())
alpha = "abcdefghijklmnopqrstuvwxyz"
emos = "🅰 🅱 🅲 🅳 🅴 🅵 🅶 🅷 🅸 🅹 🅺 🅻 🅼 🅽 🅾 🅿 🆀 🆁 🆂 🆃 🆄 🆅 🆆 🆇 🆈 🆉".replace(" ", "")
emo_map = dict(zip(alpha, emos))
def emoji_type(s):
    return "".join(emo_map.get(c, '❤️') for c in s.lower())

chain = ["rock", "paper", "fire", "water", "sponge", "lava", "ice"]

def beats(a, b, uid=None):
    if uid is None:
        uid = global_uid
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

def submit_initials(prev, guess, initials, score, uid=None):
    if uid is None:
        uid = global_uid
    url = "https://www.whatbeatsrock.com/api/scores"
    headers = {
        "User-Agent": "@meaf, on discord",
    }
    data = {"initials":initials,"score":score,"gid":uid, "text": f'{guess} {emoji_type("hello")} did not beat {prev} {emoji_type("world")}'}

    response = requests.post(url, headers=headers, json=data)
    code = response.status_code
    if code == 200:
        return True
    raise Exception(f"{response.__dict__}\n\nError {code}: \n{response._content.decode('utf-8')}")

# print(beats("rock", "paper"))
for i in range(1, len(chain)):
    print(beats(chain[i-1], chain[i]))
exit(0)
# print(beats("paper", "papers"))
# print(submit_initials("paper", "papers", "JAS", 1))

uid = "a1aa1c62-4563-11ef-b958-aa108a47b8ab"
submit_initials("thanos with a full infinity gauntlet", "Hello! Can I break the leaderboard?", "JAS", 420, uid)
exit(0)

chain = []
with open("data_gods.json") as file:
    data = json.load(file)
    chain = [God(d["name"], d["targ"]) for d in data["chain"]]

targ_score = 420
cur_score = 0
cur_str = "rock"
print(global_uid)
for i in range(len(chain)):
    if cur_score + 1 == targ_score:
        nxt = beats(cur_str, "thanos with a full infinity gauntlet")
        if not nxt:
            print("Failed thanos")
            input()
        cur_score += 1
        fin = beats("thanos with a full infinity gauntlet", "Hello! Can I break the leaderboard?")
        if fin:
            print("Failed broadcast")
            input()
        submit_initials("thanos with a full infinity gauntlet", "Hello! Can I break the leaderboard?", "JAS", targ_score)
        print("Did it!")
        input()
    assert beats(cur_str, str(chain[i]))
    cur_score += 1
    cur_str = str(chain[i])
    print(f"{cur_score} {cur_str}")
    
