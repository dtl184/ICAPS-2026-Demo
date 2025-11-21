import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected")
    quit()

js = pygame.joystick.Joystick(0)
js.init()
print("Controller:", js.get_name())
print("num axes:", js.get_numaxes())
print("num buttons:", js.get_numbuttons())
print("num hats:", js.get_numhats())

try:
    while True:
        pygame.event.pump()

        axes = [js.get_axis(i) for i in range(js.get_numaxes())]
        buttons = [js.get_button(i) for i in range(js.get_numbuttons())]
        hats = [js.get_hat(i) for i in range(js.get_numhats())]

        print(
            "axes:", ["{:.2f}".format(a) for a in axes],
            "buttons:", buttons,
            "hats:", hats,
            end="\r"
        )
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
