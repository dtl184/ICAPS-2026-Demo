import serial
import socket
import time

PORT = "/dev/ttyUSB1"
BAUD = 115200

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
COMMAND_TIMEOUT = 0.5

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

def send_velocity(ser, linear_m_s):
    speed_mm_s = int(linear_m_s * 1000.0)
    radius_mm = 0

    v_lo = speed_mm_s & 0xFF
    v_hi = (speed_mm_s >> 8) & 0xFF
    r_lo = radius_mm & 0xFF
    r_hi = (radius_mm >> 8) & 0xFF

    subpayload = bytes([0x01, 0x04, v_lo, v_hi, r_lo, r_hi])
    pkt = make_packet(subpayload)
    ser.write(pkt)

def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print(f"Listening on UDP {UDP_PORT}, driving Kobuki on {PORT}")

    last_linear = 0.0
    last_cmd_time = 0.0

    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8").strip()
                parts = msg.split()
                if len(parts) == 2:
                    last_linear = float(parts[0])
                    last_cmd_time = time.time()
                    print(f"RX from {addr}: linear={last_linear:.3f}")
            except BlockingIOError:
                pass

            now = time.time()
            if now - last_cmd_time > COMMAND_TIMEOUT:
                last_linear = 0.0

            send_velocity(ser, last_linear)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Stopping, sending zero")
        for _ in range(10):
            send_velocity(ser, 0.0)
            time.sleep(0.05)
    finally:
        ser.close()
        sock.close()

if __name__ == "__main__":
    main()
