import threading
import socket
from datetime import datetime

# Server-
HOST = "127.0.0.1"
PORT = 59000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # making the port reuse
server.bind((HOST, PORT))
server.listen()

clients = []
aliases = []

def broadcast(message):
    timestamp = datetime.now().strftime("[%H:%M] ")
    for client in clients:
        try:
            if isinstance(message, str):
                client.send(f"{timestamp}{message}".encode("utf-8"))
            else:
                client.send(message)
        except:
            index = clients.index(client)
            alias = aliases[index]
            clients.remove(client)
            aliases.remove(alias)
            client.close()
            broadcast(f"{alias} left the chat".encode("utf-8"))

def handle_client(client):
    while True:
        try:
            raw_data = client.recv(1024)
            if not raw_data:  
                raise Exception("Connection closed")
                
            try:
                message = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                print(f"Received non-UTF-8 data from {aliases[clients.index(client)]}")
                continue
                
            if message.startswith("/pm "):
                parts = message.split(" ", 2)
                if len(parts) == 3:
                    target, pm_message = parts[1], parts[2]
                    if target in aliases:
                        try:
                            target_client = clients[aliases.index(target)]
                            target_client.send(f"[PM from {aliases[clients.index(client)]}]: {pm_message}".encode("utf-8"))
                        except:
                            pass
            
            elif message == "/users":
                try:
                    client.send(f"Online users: {', '.join(aliases)}".encode("utf-8"))
                except:
                    pass
            
            else:
                broadcast(f"{aliases[clients.index(client)]}: {message}")
                
        except Exception as e:
            print(f"Error: {e}")
            try:
                index = clients.index(client)
                alias = aliases[index]
                broadcast(f"{alias} left the chat".encode("utf-8"))
                clients.remove(client)
                aliases.remove(alias)
                client.close()
            except:
                pass
            break

def receive():
    print("Server is running and listening...")
    while True:
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")
            
            client.send("alias?".encode("utf-8"))
            try:
                alias = client.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                print("Client sent invalid alias")
                client.close()
                continue
                
            aliases.append(alias)
            clients.append(client)
            
            print(f"{alias} joined the chat!")
            broadcast(f"{alias} joined the chat".encode("utf-8"))
            client.send("You are now connected!".encode("utf-8"))
            
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            
        except Exception as e:
            print(f"Server error: {e}")

if __name__ == "__main__":
    receive()