import pygame
import socket
import time

TURTLEBOT_IP = "10.5.14.114"   # <-- PUT YOUR ROBOT IP HERE
TURTLEBOT_PORT = 5005

MAX_LINEAR = 0.25      # m/s
MAX_ANGULAR = 1.5      # rad/s

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller found.")
        return

    js = pygame.joystick.Joystick(0)
    js.init()

    print("Using controller:", js.get_name())
    print("Axes =", js.get_numaxes(), "Buttons =", js.get_numbuttons())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            pygame.event.pump()

            # left stick vertical = axis 1
            ly = js.get_axis(1)
            # left stick horizontal = axis 0
            lx = js.get_axis(0)

            # deadzones
            if abs(ly) < 0.12: ly = 0.0
            if abs(lx) < 0.12: lx = 0.0

            linear = -ly * MAX_LINEAR
            angular = -lx * MAX_ANGULAR   # left = positive angular

            msg = f"{linear:.3f} {angular:.3f}"
            sock.sendto(msg.encode(), (TURTLEBOT_IP, TURTLEBOT_PORT))

            print("SEND:", msg, end="\r")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping teleop.")

    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
