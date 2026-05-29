# Multi-Client Chat & File-Share Room 💬

A real-time, multi-threaded client-server chat application featuring user registration/login (SQLite3 database auth), messaging logs, active user counts, and direct chunk-based file sharing.

---

## 📌 Objective
To build a network communication system using Python sockets where a central server coordinates multiple client connections simultaneously using multi-threading, authenticates users against an SQLite database, broadcasts text messages, and handles chunked file transfers safely.

---

## 🛠️ Tools Used
- **Language**: Python 3.7+
- **Network Interface**: `socket` library (TCP/IP connection layer)
- **Database Engine**: SQLite3 (embedded user credentials database)
- **Concurrency**: `threading` module (non-blocking server loops)
- **GUI Framework**: Tkinter

---

## 📝 Steps Performed
1. **Engineered the TCP Server** — Configured a socket listener (`server.py`) accepting TCP handshakes and launching independent worker threads for each active socket.
2. **Integrated Database Auth** — Created `auth.py` to encrypt passwords (using simple secure comparison) and store registration logs inside a local database `chat_app.db`.
3. **Structured a Network Protocol** — Implemented header parsing blocks (such as `FILE|filename|filesize` and `USERS:count`) to allow the socket to swap seamlessly between raw text data and binary files.
4. **Designed Socket File Streams** — Built file transfer routines in `client.py` using fixed-sized buffers (`4096` bytes) to write file streams directly to disk, avoiding memory overhead.
5. **Developed the Front-End** — Created a Tkinter desktop chat window (`gui.py`) with full authentication states, online users tally, messaging feeds, and file uploads.

---

## ⚡ Features
- **👥 Multi-User Broadcasts** — Any message sent by a user is instantly propagated to all other clients currently connected.
- **🔐 Secure Authentication** — Users can register a new username and password or sign in with existing credentials. Authentication status is verified by the server on SQLite database queries.
- **📥 Chunked File Transfer** — Share documents, images, or media files. Files are transferred in `4KB` chunks to avoid memory bottlenecks and saved as `received_[filename]`.
- **📊 Real-time Stats** — Displays the current count of online users actively inside the chatroom.
- **⚡ Connection Resiliency** — Handles unexpected client disconnects, cleaning up active socket ports on the server gracefully.

---

## 🚀 Installation & Run

### 📋 Prerequisites
- Python 3.7+ (uses built-in `socket`, `sqlite3`, `threading`, and `tkinter`)

### 💻 Setup & Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DhrutiM39/OIBSIP.git
   cd OIBSIP/Task4_Chat_Application
   ```

2. **Start the Central Chat Server**
   Open a terminal window and launch the server. By default, it runs on `127.0.0.1` (localhost) at port `5001`.
   ```bash
   python server.py
   ```
   *You should see the server log: `ℹ️ Server running on 127.0.0.1:5001. Waiting for connections...`*

3. **Launch the Clients**
   Open a new terminal window (or multiple windows) and start client interfaces to simulate a chat room.
   ```bash
   python gui.py
   ```

4. **Register / Log In**
   - Click **Register** if you don't have an account yet.
   - Enter your credentials, click login, and join the room!

---

## 🎮 How to Test File Transfer
1. Open the Chat Server, and open two Client GUI windows (e.g. Logged in as UserA and UserB).
2. On UserA's client, click the **📁 Send File** button.
3. Select a small text file or image.
4. UserB will receive a live notification in their chat feed: `📥 Receiving file: [filename]...` followed by `✅ File received and saved as: received_[filename]`.
5. The received file is saved directly in the client's working folder.

---

## 📁 Project Structure
```text
Task4_Chat_Application/
├── auth.py                 # SQLite database helper for user registration and validation
├── chat_app.db             # Local SQLite database file storing encrypted user logs
├── client.py               # Socket communication loops (connecting, receiving, file streams)
├── design_system.py        # Shared interface theme parameters
├── gui.py                  # Tkinter chat room UI controller (Login page and Chat page)
├── server.py               # Multithreaded TCP socket server coordinator
└── README.md               # This file
```
