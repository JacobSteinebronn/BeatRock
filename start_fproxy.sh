curl -o /home/jakesteinebronn/fproxy.py https://raw.githubusercontent.com/JacobSteinebronn/BeatRock/main/fproxy.py
cd /home/jakesteinebronn
sudo apt install python3-flask
sudo apt install python3-httpx
sudo apt install python3-aiohttp
python3 ./fproxy.py