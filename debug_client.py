import socket
import time

TURTLEBOT_IP = "172.20.10.3"   # <-- use the IP that now pings
TURTLEBOT_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(10):
    msg = f"0.2 0.0"
    sock.sendto(msg.encode("utf-8"), (TURTLEBOT_IP, TURTLEBOT_PORT))
    print("sent:", msg)
    time.sleep(0.3)
