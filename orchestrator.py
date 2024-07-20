from aiohttp import web

async def handle_register(request):
    data = await request.json()
    print(request.__dict__)

    # Here, you can process the data as needed
    print("Received data:", data)

    return web.json_response({"status": "success", "data": data})

async def init_app():
    app = web.Application()
    app.router.add_post('/register', handle_register)
    return app

if __name__ == '__main__':
    web.run_app(init_app())
