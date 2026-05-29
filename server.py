import socket
import threading
from datetime import datetime
import time

# Purpose: Configure server address and port
HOST = "127.0.0.1"
PORT = 5555

# Purpose: Create TCP socket and allow port reuse
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

clients = []
names = []

def get_time():
    return datetime.now().strftime("%H:%M")

def broadcast(message, sender=None):
    # Purpose: Send message to ALL clients except sender
    # Use sendall for guaranteed delivery of chunks
    for client in clients:
        if client != sender:
            try:
                client.sendall(message)
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def broadcast_user_count():
    time.sleep(0.05)
    count_msg = f"USERS:{len(clients)}".encode("utf-8")
    for client in clients:
        try:
            client.sendall(count_msg)
        except:
            pass

def handle_client(client, name):
    # Purpose: Handle one client — receive and broadcast messages or files
    while True:
        try:
            # We first try to read the header or normal text message
            message_data = client.recv(1024)
            if not message_data:
                break
            
            try:
                # Attempt to decode as UTF-8
                decoded_msg = message_data.decode('utf-8')
                
                if decoded_msg.startswith("FILE|"):
                    # Broadcast the file header to everyone else
                    broadcast(decoded_msg.encode('utf-8'), sender=client)
                    
                    # Parse filesize
                    parts = decoded_msg.split("|")
                    if len(parts) >= 3:
                        filename = parts[1]
                        filesize = int(parts[2])
                        
                        print(f"📥 Relaying file from {name}: {filename} ({filesize} bytes)")
                        
                        # Receive and broadcast binary chunks
                        received = 0
                        while received < filesize:
                            chunk_size = min(4096, filesize - received)
                            chunk = client.recv(chunk_size)
                            if not chunk:
                                break
                            broadcast(chunk, sender=client)
                            received += len(chunk)
                            
                        print(f"✅ File relayed: {filename}")
                else:
                    # Normal text message
                    print(f"[{get_time()}] {name}: {decoded_msg}")
                    broadcast(f"[{get_time()}] {name}: {decoded_msg}".encode("utf-8"), sender=client)
                    
            except UnicodeDecodeError:
                print(f"⚠️ Warning: Received unexpected binary data from {name}")

        except Exception as e:
            break

    # Client disconnected
    print(f"❌ {name} disconnected.")
    broadcast(f"[{get_time()}] ❌ {name} has left the chat.".encode("utf-8"))
    
    if client in clients:
        clients.remove(client)
    if name in names:
        names.remove(name)
    client.close()
    
    broadcast_user_count()

def receive_connections():
    print(f"✅ Server running on {HOST}:{PORT}")
    print("⏳ Waiting for clients...\n")

    while True:
        try:
            client, address = server.accept()
            
            client.sendall("NAME".encode("utf-8"))
            name = client.recv(1024).decode("utf-8")
            
            clients.append(client)
            names.append(name)
            
            print(f"🔌 {name} connected from {address}")
            broadcast(f"[{get_time()}] 🟢 {name} has joined the chat!".encode("utf-8"), sender=client)
            client.sendall("✅ Connected! Start typing...\n".encode("utf-8"))
            
            broadcast_user_count()
            
            thread = threading.Thread(target=handle_client, args=(client, name))
            thread.daemon = True
            thread.start()
        except:
            break

if __name__ == "__main__":
    receive_connections()
