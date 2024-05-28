import os
import socket
from multiprocessing import Pool, freeze_support
import threading
import pyperclip
import time

def ping(ip):
    response = os.system(f"ping -n 1 -w 1 {ip} > NUL")
    if response == 0:
        return ip
    return None

def get_local_devices():
    # Get the IP address of the local machine
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    # Get the prefix of the IP address
    prefix = '.'.join(ip_address.split('.')[:-1])

    # Use the ping command to find active devices on the same network
    with Pool(processes=30) as pool:
        devices = pool.map(ping, (f"{prefix}.{i}" for i in range(1, 256)))

    devices_with_names = []
    for device in devices:
        if device is not None:
            try:
                hostname, _, _ = socket.gethostbyaddr(device)
                devices_with_names.append((device, hostname))
            except socket.herror:
                devices_with_names.append((device, "Unknown"))

    return devices_with_names

def send_clipboard_data(client_socket, recents):
    while True:
        if recents != pyperclip.paste():
            recents = pyperclip.paste()
            client_socket.send(pyperclip.paste().encode())
            print("Clipboard content sent to server: " + pyperclip.paste())
        time.sleep(0.1)  # Add a small delay to reduce CPU usage

def receive_clipboard_data(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        pyperclip.copy(data)
        print("Clipboard content received from server: " + data)
        time.sleep(0.1)  # Add a small delay to reduce CPU usage

if __name__ == '__main__':
    freeze_support()

    devices = get_local_devices()
    for i, device in enumerate(devices):
        print(f"{i+1}. {device}")

    selection = int(input("Select a device: ")) - 1
    host = devices[selection][0]
    port = 24098
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    recents = pyperclip.paste()

    send_thread = threading.Thread(target=send_clipboard_data, args=(client_socket, recents))
    receive_thread = threading.Thread(target=receive_clipboard_data, args=(client_socket,))
    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()
    