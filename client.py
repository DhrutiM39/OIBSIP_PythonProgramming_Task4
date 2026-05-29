import socket
import threading
import os
import time

CHUNK_SIZE = 4096

client_socket = None

def connect_to_server(host, port, name, on_message, on_user_count, on_disconnect, on_error):
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        receive_thread = threading.Thread(
            target=receive_messages, 
            args=(name, on_message, on_user_count, on_disconnect)
        )
        receive_thread.daemon = True
        receive_thread.start()
        return True
    except Exception as e:
        on_error()
        return False

def receive_messages(name, on_message, on_user_count, on_disconnect):
    global client_socket
    while True:
        try:
            message_data = client_socket.recv(1024)
            if not message_data:
                break
            
            try:
                decoded_msg = message_data.decode("utf-8")
                
                if decoded_msg == "NAME":
                    client_socket.sendall(name.encode("utf-8"))
                elif decoded_msg.startswith("USERS:"):
                    count = decoded_msg.split(":")[1]
                    on_user_count(count)
                elif decoded_msg.startswith("FILE|"):
                    # We are receiving a file
                    _, filename, filesize = decoded_msg.split("|")
                    filesize = int(filesize)
                    
                    on_message(f"📥 Receiving file: {filename} ({filesize} bytes)...")
                    receive_file(filename, filesize)
                    on_message(f"✅ File received and saved as: received_{filename}")
                else:
                    on_message(decoded_msg)
            except UnicodeDecodeError:
                pass
        except:
            on_disconnect()
            break

def receive_file(filename, filesize):
    # Purpose: Receive file chunks and reconstruct file
    global client_socket
    received = 0
    with open(f"received_{filename}", "wb") as f:
        while received < filesize:
            chunk_size = min(CHUNK_SIZE, filesize - received)
            chunk = client_socket.recv(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    print(f"✅ File received: {filename}")

def send_message(message):
    global client_socket
    try:
        if client_socket:
            client_socket.sendall(message.encode("utf-8"))
            return True
    except:
        return False
    return False

def send_file(filepath):
    # Purpose: Send file in chunks to avoid memory overflow
    global client_socket
    try:
        if not client_socket:
            return False
            
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        # Send header first
        header = f"FILE|{filename}|{filesize}"
        client_socket.sendall(header.encode("utf-8"))
        time.sleep(0.1)   # small delay before data

        # Send file in chunks
        sent = 0
        with open(filepath, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                client_socket.sendall(chunk)
                sent += len(chunk)
                progress = (sent / filesize) * 100
                print(f"📤 Sending: {progress:.1f}%")

        print(f"✅ File sent: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error sending file: {e}")
        return False
