import requests
import uuid

url = 'http://127.0:5001/api/vs'

data = {
    'prev': 'rock',
    'guess': 'paper', 
    'gid': str(uuid.uuid4())
}

response = requests.post(url, json=data)
print(response.__dict__)