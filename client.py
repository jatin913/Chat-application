import threading
import socket

#getting the name
alias = input("Choose a username: ")

# making connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

# Receiving messages from server
def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "alias?":
                client.send(alias.encode("utf-8"))
            else:
                print(message)
        except:
            print("Disconnected from server.")
            client.close()
            break

def send_messages():
    while True:
        message = input(">> ")
        if message.startswith("/pm "):
            client.send(f"/pm {message[4:]}".encode("utf-8"))
        else:
            client.send(message.encode("utf-8"))

#threading to run each client
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()