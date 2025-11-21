import serial
import socket
import time

PORT = "/dev/ttyUSB1"    # Kobuki base
BAUD = 115200

UDP_PORT = 5005          # must match the client
UDP_IP = "0.0.0.0"       # listen on all interfaces

COMMAND_TIMEOUT = 0.5    # safety: stop if no command for this long (seconds)

def make_packet(subpayload):
    """
    Build a full Kobuki packet from a subpayload (no header/length/checksum).
    subpayload = [ID, SUB_LEN, ...data...]
    """
    header = [0xAA, 0x55]
    length = len(subpayload)

    buf = bytearray()
    buf.extend(header)
    buf.append(length)
    buf.extend(subpayload)

    # checksum: XOR of bytes from index 2 (length) to end should be 0
    cs = 0
    for b in buf[2:]:
        cs ^= b
    buf.append(cs)
    return bytes(buf)

def motors_on(ser, on=True):
    """
    Enable/disable Kobuki motors.
    ID = 0x04 (Motor Power), LEN = 2, payload=[state, 0x00]
    state = 0x01 -> on, 0x00 -> off
    """
    state = 0x01 if on else 0x00
    subpayload = bytes([0x04, 0x02, state, 0x00])
    pkt = make_packet(subpayload)
    ser.write(pkt)

def send_velocity(ser, linear_m_s):
    """
    Send a base control command to Kobuki.
    For now we ignore angular and just drive straight with radius=0.
    """
    speed_mm_s = int(linear_m_s * 1000.0)
    radius_mm = 0

    # 16-bit little endian
    v_lo = speed_mm_s & 0xFF
    v_hi = (speed_mm_s >> 8) & 0xFF
    r_lo = radius_mm & 0xFF
    r_hi = (radius_mm >> 8) & 0xFF

    # ID = 0x01 (Base Control), SUB_LEN = 4
    subpayload = bytes([0x01, 0x04, v_lo, v_hi, r_lo, r_hi])
    pkt = make_packet(subpayload)
    ser.write(pkt)

def main():
    # Open serial to Kobuki
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.1)

    # TURN MOTORS ON
    print("Enabling motors...")
    motors_on(ser, True)
    time.sleep(0.1)

    # Open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print(f"Listening for teleop commands on UDP port {UDP_PORT}...")
    print(f"Driving Kobuki on {PORT}")

    last_linear = 0.0
    last_cmd_time = 0.0

    try:
        while True:
            # Try to read any pending UDP packet
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8").strip()
                parts = msg.split()
                if len(parts) == 2:
                    last_linear = float(parts[0])
                    last_cmd_time = time.time()
                    print(f"RX from {addr}: linear={last_linear:.3f}")
            except BlockingIOError:
                pass  # no data this loop

            now = time.time()

            # Safety: if no command for a while, stop
            if now - last_cmd_time > COMMAND_TIMEOUT:
                last_linear = 0.0

            send_velocity(ser, last_linear)
            time.sleep(0.05)  # ~20 Hz

    except KeyboardInterrupt:
        print("Stopping teleop, sending zero velocity and disabling motors.")
        for _ in range(10):
            send_velocity(ser, 0.0)
            time.sleep(0.05)
        motors_on(ser, False)
        time.sleep(0.1)
    finally:
        ser.close()
        sock.close()

if __name__ == "__main__":
    main()
