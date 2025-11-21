import serial
import socket
import time

PORT = "/dev/ttyUSB1"     # Kobuki base
BAUD = 115200

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

COMMAND_TIMEOUT = 0.5   # safety timeout

def make_packet(subpayload):
    header = [0xAA, 0x55]
    length = len(subpayload)
    buf = bytearray()
    buf.extend(header)
    buf.append(length)
    buf.extend(subpayload)

    cs = 0
    for b in buf[2:]:
        cs ^= b
    buf.append(cs)
    return bytes(buf)

def motors_on(ser, on=True):
    state = 0x01 if on else 0x00
    subpayload = bytes([0x04, 0x02, state, 0x00])   # Motor Power command
    ser.write(make_packet(subpayload))

def send_velocity(ser, linear_m_s, angular_rad_s):
    speed_mm_s = int(linear_m_s * 1000.0)

    # turning radius
    if abs(angular_rad_s) < 1e-3:
        radius_mm = 0  # straight
    else:
        # spin in place if no linear velocity
        if abs(linear_m_s) < 1e-3:
            radius_mm = 1 if angular_rad_s > 0 else -1
        else:
            radius_mm = int(speed_mm_s / angular_rad_s)

    # clamp radius
    radius_mm = max(min(radius_mm, 32767), -32767)

    # little-endian fields
    v_lo = speed_mm_s & 0xFF
    v_hi = (speed_mm_s >> 8) & 0xFF
    r_lo = radius_mm & 0xFF
    r_hi = (radius_mm >> 8) & 0xFF

    subpayload = bytes([0x01, 0x04, v_lo, v_hi, r_lo, r_hi])
    ser.write(make_packet(subpayload))

def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.1)

    print("Enabling motors...")
    motors_on(ser, True)
    time.sleep(0.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print(f"Listening on UDP {UDP_PORT}")
    print(f"Driving Kobuki on {PORT}")

    last_linear = 0.0
    last_angular = 0.0
    last_cmd_time = 0.0

    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                parts = data.decode().strip().split()
                if len(parts) == 2:
                    last_linear = float(parts[0])
                    last_angular = float(parts[1])
                    last_cmd_time = time.time()
                    print(f"RX {addr} -> lin={last_linear:.3f}, ang={last_angular:.3f}")
            except BlockingIOError:
                pass

            if time.time() - last_cmd_time > COMMAND_TIMEOUT:
                last_linear = 0.0
                last_angular = 0.0

            send_velocity(ser, last_linear, last_angular)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Stopping, disabling motors")
        for _ in range(10):
            send_velocity(ser, 0.0, 0.0)
            time.sleep(0.05)
        motors_on(ser, False)

    finally:
        ser.close()
        sock.close()

if __name__ == "__main__":
    main()
