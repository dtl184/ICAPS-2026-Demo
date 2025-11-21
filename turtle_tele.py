import pygame
import socket
import time

TURTLEBOT_IP = "172.20.10.3"   # <- use the IP that pings
TURTLEBOT_PORT = 5005

FORWARD_SPEED = 0.20   # m/s
BACKWARD_SPEED = -0.20

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected")
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print("Using controller:", js.get_name())
    print("Axes:", js.get_numaxes(), "Buttons:", js.get_numbuttons())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            pygame.event.pump()

            # use the axis index that changed in joystick_debug (likely 1)
            ly = js.get_axis(1)   # left stick vertical

            # default: stop
            linear = 0.0

            # if pushed forward enough, go full 0.2 m/s
            if ly < -0.3:               # stick up
                linear = FORWARD_SPEED
            elif ly > 0.3:              # stick down
                linear = BACKWARD_SPEED

            msg = f"{linear:.3f} 0.000"
            sock.sendto(msg.encode("utf-8"), (TURTLEBOT_IP, TURTLEBOT_PORT))
            print("send:", msg, "  raw ly:", f"{ly:.2f}", end="\r")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting teleop client.")
    finally:
        js.quit()
        pygame.quit()

if __name__ == "__main__":
    main()
