import tkinter as tk
from tkinter import filedialog
import threading
import os
from datetime import datetime
import emoji
from plyer import notification
import client
import auth
from design_system import COLORS, FONTS, make_button, make_entry, center_window, show_status

HOST = "127.0.0.1"
PORT = 5555

auth.init_database()

# Client-side local message cache to simulate real multi-room separation!
active_room = "#general"
room_messages = {
    "#general": [
        ("System", "Welcome to #general! Connect, chat, and collaborate with your peers.", "00:00", False)
    ],
    "#coding": [
        ("System", "Welcome to #coding! Share snippets, ask bugs, and talk python.", "00:00", False)
    ],
    "#memes": [
        ("System", "Welcome to #memes! Keep it light and share your best tech jokes.", "00:00", False)
    ]
}

# Active room buttons dictionary
room_buttons = {}
chat_inner_frame = None
chat_canvas = None
room_header_label = None

# Purpose: Translates text shortcodes like :smile: into graphical emojis
def process_emojis(text):
    return emoji.emojize(text, language="alias")

# Purpose: Triggers standard Windows desktop popups when window lacks focus
def show_notification(title, message):
    try:
        notification.notify(title=title, message=message, timeout=4)
    except Exception as e:
        print(f"Notification error: {e}")

# Purpose: Builds and shows the main chat workspace
def open_chat_gui(username):
    global chat_inner_frame, chat_canvas, room_header_label
    
    window = tk.Tk()
    window.title("💬 Chat App")
    center_window(window, 900, 650)
    window.resizable(False, False)
    window.configure(bg=COLORS["bg_dark"])

    # Main 3-Panel Layout Container
    main_frame = tk.Frame(window, bg=COLORS["bg_dark"])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # ---------------- 1. LEFT PANEL: ROOMS SIDEBAR ----------------
    rooms_frame = tk.Frame(main_frame, bg=COLORS["bg_card"], width=200)
    rooms_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    rooms_frame.pack_propagate(False)
    
    # Left sidebar Title
    tk.Label(rooms_frame, text="💬 OIBSIP SERVER", font=FONTS["heading"], bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(15, 10), padx=15, anchor="w")
    tk.Label(rooms_frame, text="CHANNELS", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(pady=(5, 5), padx=15, anchor="w")
    
    # Purpose: Re-draws message bubbles for selected active room
    def switch_room(room_name):
        global active_room
        if active_room == room_name:
            return
            
        active_room = room_name
        room_header_label.config(text=f"{room_name}")
        
        # Color highlighted active room button
        for name, btn in room_buttons.items():
            if name == room_name:
                btn.config(bg=COLORS["bg_hover"], fg=COLORS["text_primary"])
            else:
                btn.config(bg=COLORS["bg_card"], fg=COLORS["text_secondary"])
                
        # Clear middle panel and redraw the selected room's message log
        for w in chat_inner_frame.winfo_children():
            w.destroy()
            
        for sender, text, timestamp, is_own in room_messages[room_name]:
            render_bubble(sender, text, timestamp, is_own)

    # Build room listing buttons
    for r_name in ["#general", "#coding", "#memes"]:
        btn = tk.Button(
            rooms_frame, text=f"  {r_name}", font=FONTS["body"],
            bg=COLORS["bg_hover"] if r_name == active_room else COLORS["bg_card"],
            fg=COLORS["text_primary"] if r_name == active_room else COLORS["text_secondary"],
            activebackground=COLORS["bg_hover"], activeforeground=COLORS["text_primary"],
            relief="flat", bd=0, anchor="w", cursor="hand2", padx=10, pady=8
        )
        btn.config(command=lambda name=r_name: switch_room(name))
        btn.pack(fill=tk.X, pady=2, padx=10)
        room_buttons[r_name] = btn

    # ---------------- 2. MIDDLE PANEL: MESSAGES AREA ----------------
    msg_container = tk.Frame(main_frame, bg=COLORS["bg_dark"])
    msg_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Active Channel Header
    channel_header = tk.Frame(msg_container, bg=COLORS["bg_card"], height=50)
    channel_header.pack(fill=tk.X, pady=(0, 10))
    channel_header.pack_propagate(False)
    
    room_header_label = tk.Label(channel_header, text=active_room, font=FONTS["heading"], bg=COLORS["bg_card"], fg=COLORS["text_primary"])
    room_header_label.pack(side=tk.LEFT, padx=15, pady=12)

    # Scrollable bubble canvas frame
    chat_canvas = tk.Canvas(msg_container, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(msg_container, orient="vertical", command=chat_canvas.yview)
    chat_inner_frame = tk.Frame(chat_canvas, bg=COLORS["bg_dark"])
    
    chat_inner_frame.bind(
        "<Configure>",
        lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
    )
    canvas_window = chat_canvas.create_window((0, 0), window=chat_inner_frame, anchor="nw")
    
    def match_width(e):
        chat_canvas.itemconfig(canvas_window, width=e.width)
    chat_canvas.bind("<Configure>", match_width)
    
    chat_canvas.configure(yscrollcommand=scrollbar.set)
    
    chat_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Padded Input Toolbar
    input_frame = tk.Frame(msg_container, bg=COLORS["bg_card"], height=65)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    input_frame.pack_propagate(False)

    message_entry = make_entry(input_frame, placeholder="Type a message here...")
    message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Purpose: Opens standard select dialog, triggers background transfer thread
    def browse_and_send_file():
        filepath = filedialog.askopenfilename(title="Select File to Share")
        if filepath:
            filename = os.path.basename(filepath)
            # Run upload in a thread so socket write doesn't hang UI
            threading.Thread(target=client.send_file, args=(filepath,), daemon=True).start()
            add_chat_msg("You", f"📤 Sent File: {filename}", "Now", is_own=True)

    attach_btn = make_button(input_frame, "📎 Attach", browse_and_send_file, style="ghost")
    attach_btn.pack(side=tk.LEFT, padx=(0, 5), pady=10)

    send_btn = make_button(input_frame, "Send ➤", lambda: send_message(), style="secondary")
    send_btn.pack(side=tk.LEFT, padx=(0, 10), pady=10)

    message_entry.bind("<Return>", lambda e: send_message())

    # ---------------- 3. RIGHT PANEL: MEMBERS LIST ----------------
    users_frame = tk.Frame(main_frame, bg=COLORS["bg_card"], width=200)
    users_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
    users_frame.pack_propagate(False)
    
    users_title = tk.Label(users_frame, text="ONLINE MEMBERS", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"])
    users_title.pack(pady=(15, 10), padx=15, anchor="w")
    
    user_list_frame = tk.Frame(users_frame, bg=COLORS["bg_card"])
    user_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
    
    # Initialize the local current user label
    tk.Label(user_list_frame, text=f"🟢 {username} (You)", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=4, anchor="w")

    # Purpose: Instantiates custom styled text bubbles into active inner frame
    def render_bubble(sender, text, timestamp, is_own=False):
        text = process_emojis(text)
        bubble_row = tk.Frame(chat_inner_frame, bg=COLORS["bg_dark"])
        bubble_row.pack(fill=tk.X, pady=4)
        
        if is_own:
            bg_color, anchor, side = COLORS["primary"], "e", tk.RIGHT
            text_fg = COLORS["text_primary"]
            meta_fg = COLORS["primary_light"]
        else:
            bg_color, anchor, side = COLORS["bg_card"], "w", tk.LEFT
            text_fg = COLORS["text_primary"]
            meta_fg = COLORS["text_secondary"]
            
        bubble_card = tk.Frame(bubble_row, bg=bg_color, padx=12, pady=8, bd=0)
        bubble_card.pack(side=side, padx=10)
        
        # Bubble Header: Sender + Time
        tk.Label(bubble_card, text=f"{sender} • {timestamp}", font=FONTS["small"], bg=bg_color, fg=meta_fg).pack(anchor=anchor)
        
        # Message content bubble text
        tk.Message(
            bubble_card, text=text, font=FONTS["body"], bg=bg_color, fg=text_fg,
            width=280, justify="left" if side == tk.LEFT else "right"
        ).pack(anchor=anchor, pady=(2, 0))
        
        # Scroll canvas down
        chat_canvas.update_idletasks()
        chat_canvas.yview_moveto(1.0)

    # Purpose: Appends message to local cache and renders if current room matches active
    def add_chat_msg(sender, text, timestamp, is_own=False, room="#general"):
        room_messages[room].append((sender, text, timestamp, is_own))
        if room == active_room:
            render_bubble(sender, text, timestamp, is_own)

    # Purpose: Receives messages from client networking socket thread
    def on_message_received(message):
        now_time = datetime.now().strftime("%H:%M")
        
        # Format parser to unpack "[12:30] Bob: Hey!"
        if "]" in message and ":" in message:
            try:
                time_part = message.split("]")[0][1:]
                rest = message.split("]")[1].strip()
                sender = rest.split(":")[0]
                text = ":".join(rest.split(":")[1:]).strip()
                
                # Check for client-side room routing prefix tags like "#coding | Hello!"
                target_room = "#general"
                for r_name in room_messages.keys():
                    if text.startswith(r_name):
                        target_room = r_name
                        text = text.replace(r_name, "").strip(" |").strip()
                        break
                        
                add_chat_msg(sender, text, time_part, is_own=False, room=target_room)
            except:
                add_chat_msg("System", message, now_time, is_own=False, room=active_room)
        else:
            add_chat_msg("System", message, now_time, is_own=False, room=active_room)
            
        if not window.focus_displayof():
            show_notification("💬 Chat App", message[:50])

    # Purpose: Handles update events for active online server connections count
    def on_user_count_update(count):
        users_title.config(text=f"MEMBERS — {count} ONLINE")
        # Clear online users list and redraw
        for widget in user_list_frame.winfo_children():
            widget.destroy()
        tk.Label(user_list_frame, text=f"🟢 {username} (You)", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=4, anchor="w")
        for i in range(1, int(count)):
            tk.Label(user_list_frame, text=f"🟢 Peer Member {i}", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(pady=4, anchor="w")

    # Purpose: Handles disconnect callback events from server
    def on_disconnect():
        add_chat_msg("System", "❌ Server connection lost.", "Now", is_own=False, room=active_room)

    # Purpose: Handles setup connection failure callbacks
    def on_error():
        add_chat_msg("System", "❌ Socket failed to reach host!", "Now", is_own=False, room=active_room)

    # Purpose: Dispatches message requests through TCP socket
    def send_message():
        text = message_entry.get().strip()
        if not text or text == "Type a message here...":
            return
            
        # Standardize room prefix tags so server broadcasts and clients route correctly
        # Send message with room prefix tag!
        full_msg = f"{active_room} | {text}"
        success = client.send_message(full_msg)
        if success:
            add_chat_msg("You", text, datetime.now().strftime("%H:%M"), is_own=True, room=active_room)
            message_entry.delete(0, tk.END)
        else:
            add_chat_msg("System", "❌ Connection closed. Send failed.", "Now", is_own=False, room=active_room)

    # Draw general room greeting bubble initially
    render_bubble("System", "Welcome to #general! Connect, chat, and collaborate with your peers.", "00:00", False)
    
    # Establish real TCP socket connection
    client.connect_to_server(HOST, PORT, username, on_message_received, on_user_count_update, on_disconnect, on_error)
    window.mainloop()

# Purpose: Builds the secure registration/login launch portal
def show_login_window():
    login_window = tk.Tk()
    login_window.title("💬 Chat Login")
    center_window(login_window, 400, 560)
    login_window.resizable(False, False)
    login_window.configure(bg=COLORS["bg_dark"])

    # Header Card
    tk.Label(login_window, text="💬", font=("Segoe UI Emoji", 40), bg=COLORS["bg_dark"]).pack(pady=(40, 5))
    tk.Label(login_window, text="Chat Application", font=FONTS["title"], bg=COLORS["bg_dark"], fg=COLORS["text_primary"]).pack()
    tk.Label(login_window, text="Connect. Chat. Collaborate.", font=FONTS["subtitle"], bg=COLORS["bg_dark"], fg=COLORS["text_secondary"]).pack(pady=(0, 25))

    # Inputs Frame
    input_frame = tk.Frame(login_window, bg=COLORS["bg_dark"])
    input_frame.pack(fill=tk.X, padx=40)

    tk.Label(input_frame, text="👤 USERNAME", font=FONTS["small"], bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(10, 2))
    username_entry = make_entry(input_frame, placeholder="Enter username")
    username_entry.pack(fill=tk.X, ipady=8)

    tk.Label(input_frame, text="🔒 PASSWORD", font=FONTS["small"], bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(15, 2))
    password_entry = make_entry(input_frame, placeholder="Enter password", show="*")
    password_entry.pack(fill=tk.X, ipady=8)

    # Feedback Notification Area
    msg_label = tk.Label(login_window, text="", font=FONTS["small"], bg=COLORS["bg_dark"])
    msg_label.pack(pady=15)

    # Purpose: Validates credential input and performs system authentication
    def handle_login():
        username = username_entry.get().strip()
        password = password_entry.get()
        if username == "Enter username" or password == "Enter password" or not username or not password:
            show_status(msg_label, "⚠️ Please fill all input fields", COLORS["warning"])
            return
            
        result = auth.login_user(username, password)
        if "✅" in result:
            show_status(msg_label, result, COLORS["success"])
            login_window.after(1000, lambda: [login_window.destroy(), open_chat_gui(username)])
        else:
            show_status(msg_label, result, COLORS["danger"])

    # Purpose: Registers new credentials into database safely
    def handle_register():
        username = username_entry.get().strip()
        password = password_entry.get()
        if username == "Enter username" or password == "Enter password" or not username or not password:
            show_status(msg_label, "⚠️ Please fill all input fields", COLORS["warning"])
            return
            
        result = auth.register_user(username, password)
        if "✅" in result:
            show_status(msg_label, result, COLORS["success"])
        else:
            show_status(msg_label, result, COLORS["danger"])

    login_btn = make_button(login_window, "🔓 Login to Account", handle_login, style="primary")
    login_btn.pack(fill=tk.X, padx=40, pady=(10, 5))
    
    # Registration Redirect Frame
    reg_frame = tk.Frame(login_window, bg=COLORS["bg_dark"])
    reg_frame.pack(pady=10)
    tk.Label(reg_frame, text="Don't have an account?", font=FONTS["small"], bg=COLORS["bg_dark"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
    reg_btn = tk.Button(reg_frame, text="Register Now →", command=handle_register, bg=COLORS["bg_dark"], fg=COLORS["secondary"], activebackground=COLORS["bg_dark"], activeforeground=COLORS["primary_light"], font=("Segoe UI", 9, "bold", "underline"), relief="flat", bd=0, cursor="hand2")
    reg_btn.pack(side=tk.LEFT, padx=5)

    login_window.mainloop()

if __name__ == "__main__":
    show_login_window()
