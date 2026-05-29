import tkinter as tk

COLORS = {
    "bg_dark"     : "#0f0f1a",   # main window
    "bg_card"     : "#1a1a2e",   # cards/panels
    "bg_surface"  : "#16213e",   # input fields
    "bg_hover"    : "#0f3460",   # hover state
    "primary"     : "#7c3aed",   # purple — main action
    "primary_light": "#a855f7",  # lighter purple
    "secondary"   : "#06b6d4",   # cyan — secondary action
    "success"     : "#22c55e",   # green
    "warning"     : "#f59e0b",   # amber
    "danger"      : "#ef4444",   # red
    "text_primary" : "#ffffff",
    "text_secondary": "#94a3b8",
    "text_muted"   : "#475569"
}

FONTS = {
    "title"    : ("Segoe UI", 24, "bold"),
    "subtitle" : ("Segoe UI", 14),
    "heading"  : ("Segoe UI", 16, "bold"),
    "body"     : ("Segoe UI", 11),
    "small"    : ("Segoe UI", 9),
    "mono"     : ("Courier New", 12, "bold"),  # for passwords/code
    "emoji"    : ("Segoe UI Emoji", 20)
}

def add_hover(btn, color_in, color_out):
    # Purpose: Add interactive hover highlights to buttons
    btn.bind("<Enter>", lambda e: btn.config(bg=color_in))
    btn.bind("<Leave>", lambda e: btn.config(bg=color_out))

def make_button(parent, text, command, style="primary", width=None):
    # Purpose: Reusable flat button with dynamic hover states
    styles = {
        "primary"  : {"bg": "#7c3aed", "fg": "#ffffff", "activebackground": "#6d28d9"},
        "secondary": {"bg": "#06b6d4", "fg": "#ffffff", "activebackground": "#0891b2"},
        "danger"   : {"bg": "#ef4444", "fg": "#ffffff", "activebackground": "#dc2626"},
        "ghost"    : {"bg": "#1a1a2e", "fg": "#94a3b8", "activebackground": "#0f3460"}
    }
    s = styles.get(style, styles["primary"])
    
    kwargs = {
        "text": text,
        "command": command,
        "bg": s["bg"],
        "fg": s["fg"],
        "activebackground": s["activebackground"],
        "activeforeground": "#ffffff",
        "font": ("Segoe UI", 11, "bold"),
        "relief": "flat",
        "bd": 0,
        "padx": 20,
        "pady": 10,
        "cursor": "hand2"
    }
    if width is not None:
        kwargs["width"] = width
        
    btn = tk.Button(parent, **kwargs)
    add_hover(btn, s["activebackground"], s["bg"])
    return btn

def make_entry(parent, placeholder="", show=""):
    # Purpose: Reusable input field with focus placeholder handling
    entry = tk.Entry(
        parent,
        bg="#16213e", fg="#ffffff",
        insertbackground="#7c3aed",
        relief="flat", bd=0,
        font=("Segoe UI", 11)
    )
    
    # Placeholder logic
    entry.insert(0, placeholder)
    entry.config(fg="#475569")
    
    if show:
        entry.config(show="")

    def on_focus_in(e):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#ffffff")
            if show:
                entry.config(show=show)

    def on_focus_out(e):
        if entry.get() == "":
            if show:
                entry.config(show="")
            entry.insert(0, placeholder)
            entry.config(fg="#475569")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return entry

def center_window(window, width, height):
    # Purpose: Center window dynamically on screen
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_status(label, text, color, duration=3000):
    # Purpose: Display feedback messages that fade out automatically after duration ms
    label.config(text=text, fg=color)
    label.after(duration, lambda: label.config(text=""))
