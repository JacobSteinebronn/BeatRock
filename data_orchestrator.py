from aiohttp import web
import asyncio
import httpx
import uuid
import json
import random
import traceback
import sys

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
            print("A proxy is now among us...")
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
            json.dump({"chain": [g.to_json() for g in self.chain]}, file)

    def get_resumers(self):
        last = self.chain[-1]
        return God(last.targ, "__NOTHING"), last

state = State()

class NoProxyException(Exception):
    pass

async def push_proxy(uid, host):
    global proxy_wait_task

    if (uid, host) not in proxies:
        print(f"Registered proxy {uid} at {host}")
        proxies.append((uid, host))
    
    if proxy_wait_task is not None:
        proxy_wait_task.cancel()
        proxy_wait_task = None

async def delay_push_proxy(uid, host):
    await asyncio.sleep(600)
    print(f"Re-pushing proxy {uid} {host}")
    await push_proxy(uid, host)

async def query_proxy(path, data):
    while True:
        if len(proxies) == 0: raise NoProxyException()  # TODO: Handle this in main() by just sleeping for a while
        uuid, host = proxies.pop(0)
        try:
            response = await client.post(f"http://{host}:8080/{path}", json=data, timeout=20)
        except httpx.RemoteProtocolError:
            print("Proxy didn't respond, so I'm ditching it")
            continue
        except httpx.ConnectError:
            print(f"Couldn't connect to proxy {host}, so I'm ditching it")
            continue
        except httpx.ReadTimeout:
            print(f"Proxy {host} timed out, so I'm ditching it")
            continue
        except:
            sys.exit(traceback.print_exc())

        content_json = json.loads(response._content.decode("utf-8"))
        if response.status_code == 200:
            proxies.append((uuid, host))
            print(f"200 from {host}, {content_json['data']['guess_wins']}")
            return content_json
        if response.status_code == 404:
            print(f"404 from {uuid} {host}, dropping this proxy, {response.__dict__}")
            continue
        if response.status_code == 418:
            print(f"418 from {uuid} {host}, delay-queueing this proxy")
            bg_tasks.append(asyncio.create_task(delay_push_proxy(uuid, host)))
        if response.status_code == 400:
            proxies.append((uuid, host))
            print(f"400 from {host}, {content_json}")
            return {"data": {"guess_wins": False}}
        
        # Idk what this is, so we'll just drop the proxy
        print(response.__dict__)
            
async def beats(prev, guess, gid=None):
    global global_gid
    if gid == None: gid = global_gid
    while True:
        try:
            resp_data = await query_proxy("api/vs", {"prev": prev, "guess": guess, "gid": gid})
            return resp_data["data"]["guess_wins"]
        except NoProxyException:
            print("We ran out of proxies, so I'll wait for some to pull up")
            await wait_for_proxies()

async def restart_and_resume():
    global_gid = str(uuid.uuid4())
    first, second = state.get_resumers()
    win_1 = await beats("rock", str(first))
    win_2 = await beats(str(first), str(second))

async def background_task():
    print("Starting up, waiting for proxies")
    await wait_for_proxies()
    print("Got proxies!")
    await restart_and_resume()
    print("Starting event loop")
    while True:
        # We have an active game and we just beat the last guy
        nxt = state.gen_next()
        if await beats(str(state.chain[-1]), str(nxt)):
            state.append(nxt)
            continue
        else:
            await restart_and_resume()
            continue

async def handle_register(request):
    data = await request.json()

    proxy_host, _ = request._transport_peername
    proxy_uuid = data["proxy_uuid"]
    await push_proxy(proxy_uuid, proxy_host)

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
    web.run_app(init_app(), port=8080)
