import pygame
import socket
import time

TURTLEBOT_IP = "10.5.14.114"   # <-- PUT YOUR TURTLEBOT'S IP HERE
TURTLEBOT_PORT = 5005

# Max speeds (tune these!)
MAX_LINEAR = 0.3   # m/s
MAX_ANGULAR = 1.0  # rad/s

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected. Plug in the Xbox controller and try again.")
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Using controller: {js.get_name()}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            pygame.event.pump()

            # Typical Xbox mapping in pygame:
            # axis 1: left stick vertical (up = -1, down = +1)
            # axis 0: left stick horizontal
            # axis 4: right stick horizontal (on some controllers)
            # We'll use left stick Y for linear, left stick X for angular
            ly = js.get_axis(1)   # forward/back
            lx = js.get_axis(0)   # left/right turn

            # Deadzone
            if abs(ly) < 0.15:
                ly = 0.0
            if abs(lx) < 0.15:
                lx = 0.0

            # Map to velocities
            linear = -ly * MAX_LINEAR      # up on stick = forward
            angular = -lx * MAX_ANGULAR    # left on stick = positive turn

            # pack as simple text "v omega"
            msg = f"{linear:.3f} {angular:.3f}"
            sock.sendto(msg.encode("utf-8"), (TURTLEBOT_IP, TURTLEBOT_PORT))

            time.sleep(0.03)  # ~30 Hz

    except KeyboardInterrupt:
        print("Exiting teleop client.")
    finally:
        js.quit()
        pygame.quit()

if __name__ == "__main__":
    main()
