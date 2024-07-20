import httpx
import asyncio
from quart import Quart, request, jsonify
import signal
import sys

app = Quart(__name__)

@app.route('/<path:path>', methods=['POST'])
async def post_handler(path):
    data = await request.get_json()
    response = {
        'message': f'Data received successfully on path: {path}',
        'received_data': data
    }
    return jsonify(response), 200

async def periodic_task(interval):
    try:
        while True:
            print("Periodic task running...")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("Periodic task cancelled.")

async def send_post_request():
    url = 'http://127.0.0.1:5000/test'
    data = {
        'key': 'value'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)

    if response.status_code == 200:
        print('Response received:')
        print(response.json())
    else:
        print(f'Failed to receive valid response. Status code: {response.status_code}')

async def main():
    # app_task = asyncio.create_task(app.run_task(debug=True))
    periodic_task_task = asyncio.create_task(periodic_task(5))

    # Send the POST request after a short delay to ensure the server is up
    await asyncio.sleep(1)
    # await send_post_request()

    # Run both tasks concurrently
    try:
        await asyncio.gather(periodic_task_task)
    except asyncio.CancelledError:
        print("Main task cancelled, shutting down.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Handle shutdown signals (Ctrl+C)
    def signal_handler(sig, frame):
        print("Received shutdown signal.")
        loop.stop()

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), signal_handler, getattr(signal, signame), None)

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Shutdown requested.")
    finally:
        # Cancel all running tasks
        tasks = asyncio.all_tasks(loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        print("Shutdown complete.")