from aiohttp import web
import asyncio
import httpx
import uuid
import json
import random
import traceback
import sys
import datetime

proxies = []
client = httpx.AsyncClient()
bg_tasks = []  # I don't think we'll ever really use these
global_gid = str(uuid.uuid4())

proxy_wait_task = None

async def wait_for_proxies():
    global proxy_wait_task
    while True:
        if len(proxies): 
            proxy_wait_task = None
            print("A proxy is now among us...", flush=True)
            return
        if proxy_wait_task is not None: 
            try: await proxy_wait_task
            except asyncio.CancelledError: pass
            proxy_wait_task = None
        else: proxy_wait_task = asyncio.create_task(asyncio.sleep(300))

class God:
    def __init__(self, name, targ):
        self.name = name
        self.targ = targ
    
    def __str__(self):
        if self.targ == "__NOTHING": return f"A person named {self.name} who breaks rocks"
        return f"A person named {self.name} who is stronger, smarter, and faster than {self.targ}"

    def to_json(self): return {"name": self.name, "targ": self.targ}
    def to_compact(self): return f"{self.name}>{self.targ}"

class State:
    def __init__(self):
        with open("data_gods.json") as file:
            self.chain = [God(d["name"], d["targ"]) for d in json.load(file)["chain"]]
        with open("names.txt") as file:
            self.names = [line.strip() for line in file.readlines()]
        self.compacts = {g.to_compact() for g in self.chain}

    def gen_next(self):
        prev_name = self.chain[-1].name
        for tries in range(100):
            nxt = God(self.names[random.randint(0, len(self.names)-1)], prev_name)
            if nxt.to_compact() in self.compacts: continue
            return nxt

    def append(self, god):
        self.compacts.add(god.to_compact())
        self.chain.append(god)
        with open("data_gods.json", "w") as file:
            json.dump({"chain": [g.to_json() for g in self.chain]}, file, indent=2)

    def get_resumers(self):
        last = self.chain[-1]
        return God(last.targ, "__NOTHING"), last

state = State()

class NoProxyException(Exception):
    pass

def push_proxy(host, silent=True):
    global proxy_wait_task

    if host not in proxies:
        if not silent: print(f"Registered proxy at {host}", flush=True)
        proxies.append(host)
    
    if proxy_wait_task is not None:
        proxy_wait_task.cancel()
        proxy_wait_task = None

async def delay_push_proxy(host):
    await asyncio.sleep(600)
    print(f"Re-pushing proxy {host}", flush=True)
    push_proxy(host)

async def query_with_hard_timeout(url, json, timeout=20):
    ctask = asyncio.create_task(asyncio.sleep(timeout))
    ptask = asyncio.create_task(client.post(url, json=json, timeout=timeout))

    done, pending = await asyncio.wait([ctask, ptask], return_when=asyncio.FIRST_COMPLETED)
    for task in pending: task.cancel()
    result = None
    for task in done: result = result or task.result()
    return result

async def query_proxy(path, data):
    while True:
        if len(proxies) == 0: raise NoProxyException()  # TODO: Handle this in main() by just sleeping for a while
        host = proxies.pop(0)
        try:
            print(f"[{datetime.datetime.now()}]Querying {host}", flush=True)
            response = await query_with_hard_timeout(f"http://{host}:8080/{path}", json=data, timeout=20)
            if response is None:
                print(f"Proxy {host} hit the hard timeout, so I'm ditching it", flush=True)
                continue
        except httpx.RemoteProtocolError:
            print("Proxy didn't respond, so I'm ditching it", flush=True)
            continue
        except httpx.ConnectError:
            print(f"Couldn't connect to proxy {host}, so I'm ditching it", flush=True)
            continue
        except httpx.ReadTimeout:
            print(f"Proxy {host} timed out, so I'm ditching it", flush=True)
            continue
        except:
            print("Dammit!")
            sys.exit(traceback.print_exc())

        try:
            content_json = json.loads(response._content.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"Couldn't parse the response from {host}, which means the game and proxy are dead")
            return None

        if response.status_code == 200:
            push_proxy(host)
            print(f"200 from {host}, {content_json['data']['guess_wins']}", flush=True)
            return content_json
        if response.status_code == 404:
            print(f"404 from {host}, dropping this proxy, {response.__dict__}", flush=True)
            continue
        if response.status_code == 418:
            bg_tasks.append(asyncio.create_task(delay_push_proxy(host)))
            print(f"418: {content_json}", flush=True)
            print(f"418 from {host}, delay-queueing this proxy", flush=True)
            continue
        if response.status_code == 400:
            push_proxy(host)
            print(f"400 from {host}, {content_json}", flush=True)
            return None
        if response.status_code == 503:
            push_proxy(host)
            print(f"503 from {host}, which means our game is dead but the proxy is fine", flush=True)
            return None

        
        # Idk what this is, so we'll just drop the proxy
        print(response.__dict__, flush=True)
            
async def beats(prev, guess, gid=None):
    global global_gid
    if gid == None: gid = global_gid
    while True:
        try:
            resp_data = await query_proxy("api/vs", {"prev": prev, "guess": guess, "gid": gid})
            if resp_data is None: return False
            return resp_data["data"]["guess_wins"]
        except NoProxyException:
            print("We ran out of proxies, so I'll wait for some to pull up", flush=True)
            await wait_for_proxies()

async def submit_initials(prev, guess, initials, score, gid=None):
    if gid is None: gid = global_gid
    url = "https://www.whatbeatsrock.com/api/scores"
    headers = {
        "User-Agent": "@meaf, on discord",
    }
    data = {"initials":initials,"score":score,"gid":gid, "text": f'{guess} 🐶👋 did not beat {prev} 💪😈'}

    response = await client.post(url, headers=headers, json=data)
    code = response.status_code
    if code == 200: return True
    raise Exception(f"{response.__dict__}\n\nError {code}: \n{response._content.decode('utf-8')}")

thanos = "Thanos with a full infinity gauntlet"
banner = "Hi there! It's me, @meaf :)"

async def background_task():
    try:
        print("Starting up, waiting for proxies", flush=True)
        await wait_for_proxies()
        print("Got proxies!", flush=True)
        cur_score = 0
        targ_score = 10
        print("Starting event loop", flush=True)
        cur_str = "rock"
        for i in range(len(state.chain)):
            if i % 20 == 0: print(global_gid)
            if i + 1 == targ_score:
                print(f"Closing in! {global_gid}")
                if not await beats(cur_str, thanos):
                    print("Didn't win with thanos, really?")
                    exit(0)
                if await beats(thanos, banner):
                    print("We won with our banner??")
                    exit(0)
                dun = await submit_initials(thanos, banner, "JAS", targ_score)
                print(f"Wahoo????:{dun}")
                exit(0)
            assert await beats(cur_str, str(state.chain[i])), "Failed something shoulda been cached"
            cur_score += 1
            cur_str = str(state.chain[i])
            print(f"{cur_score} {cur_str}")

                
                
    except:
        print("Come on!")
        sys.exit(traceback.print_exc())

async def handle_register(request):
    data = await request.json()

    proxy_host, _ = request._transport_peername
    proxy_uuid = data["proxy_uuid"]
    push_proxy(proxy_host, silent=False)

    return web.json_response({"status": "success", "data": data})

async def init_app():
    app = web.Application()
    app.router.add_post('/register', handle_register)

    app.on_startup.append(start_background_task)
    app.on_cleanup.append(stop_background_task)

    return app

async def start_background_task(app): app['background_task'] = asyncio.create_task(background_task())

async def stop_background_task(app):
    app['background_task'].cancel()
    try: await app['background_task']
    except asyncio.CancelledError: pass

if __name__ == '__main__':
    web.run_app(init_app(), port=8081)
