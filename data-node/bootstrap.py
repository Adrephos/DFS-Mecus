import subprocess

AWS = False
MY_IP = '127.0.0.1'


if AWS:
    ip = subprocess.run(["curl", "ip.me"], stdout=subprocess.PIPE, text=True,)
    MY_IP = ip.stdout.strip('\n')

PORT = '5000'
NAME = 'DataNode1'
URL = 'http://3.208.82.202:5000/'
URL_SLAVE = 'http://100.24.82.225:5000/'
KEEPALIVE_SLEEP_SECONDS = 5
