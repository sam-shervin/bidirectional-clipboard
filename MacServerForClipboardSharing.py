import socket
import pyperclip
import time
import threading

def send_data(conn, recents):
    while True:
        if recents != pyperclip.paste():
            recents = pyperclip.paste()
            conn.send(pyperclip.paste().encode())
            print("Sent: " + pyperclip.paste())
        time.sleep(0.1)  # Add a small delay to reduce CPU usage


def receive_data(conn):
    while True:
        data = conn.recv(1024).decode()
        pyperclip.copy(data)
        print("Received: " + pyperclip.paste())
        time.sleep(0.1)  # Add a small delay to reduce CPU usage


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 24098))
server_socket.listen(1)
print("Listening on port 24098")
recents = pyperclip.paste()

while True:
    conn, addr = server_socket.accept()
    print("Connected to " + addr[0])
    break

send_thread = threading.Thread(target=send_data, args=(conn, recents))
receive_thread = threading.Thread(target=receive_data, args=(conn,))

# Start the threads
send_thread.start()
receive_thread.start()

# Wait for both threads to finish
send_thread.join()
receive_thread.join()
        
        