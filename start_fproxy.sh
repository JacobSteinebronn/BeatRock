curl -o /home/jakesteinebronn/fproxy.py https://raw.githubusercontent.com/JacobSteinebronn/BeatRock/main/fproxy.py
cd /home/jakesteinebronn
sudo apt install python3-flask -y
sudo apt install python3-httpx -y
sudo apt install python3-aiohttp -y
python3 ./fproxy.py