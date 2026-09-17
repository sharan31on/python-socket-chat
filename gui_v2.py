import os
import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, filedialog

HOST = '10.111.221.55'  # Your PC's IPv4 address
PORT = 65432

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Socket Chat - File Sharing")
        self.root.geometry("820x560")
        self.root.configure(bg="#202225")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        if not self.username:
            self.root.destroy()
            return

        self.create_widgets()
        self.setup_tags()

        try:
            self.sock.connect((HOST, PORT))
            self.sock.sendall(self.username.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{e}")
            self.root.destroy()
            return

        self.listen_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.listen_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_tags(self):
        self.chat_area.tag_config("time", foreground="#72767d", font=("Arial", 8))
        self.chat_area.tag_config("self", foreground="#58a6ff", font=("Arial", 10, "bold"))
        self.chat_area.tag_config("server", foreground="#faa61a", font=("Arial", 9, "italic"))
        self.chat_area.tag_config("whisper", foreground="#f47fff", font=("Arial", 10, "italic"))
        self.chat_area.tag_config("file", foreground="#3ba55d", font=("Arial", 10, "bold"))
        self.chat_area.tag_config("normal", foreground="#dcddde", font=("Arial", 10))

    def create_widgets(self):
        header = tk.Label(
            self.root, 
            text=f"Chat Room — Logged in as: {self.username}", 
            bg="#2f3136", 
            fg="white", 
            font=("Arial", 11, "bold"), 
            pady=10
        )
        header.pack(fill=tk.X)

        main_frame = tk.Frame(self.root, bg="#202225")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=4)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.chat_area = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            bg="#36393f", 
            fg="white", 
            font=("Arial", 10),
            state='disabled', 
            padx=10, 
            pady=10
        )
        self.chat_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        user_frame = tk.Frame(main_frame, bg="#2f3136")
        user_frame.grid(row=0, column=1, sticky="nsew")

        user_title = tk.Label(
            user_frame, 
            text="ONLINE USERS", 
            bg="#2f3136", 
            fg="#8e9297", 
            font=("Arial", 9, "bold"), 
            pady=6
        )
        user_title.pack(fill=tk.X)

        self.user_listbox = tk.Listbox(
            user_frame, 
            bg="#2f3136", 
            fg="#43b581", 
            font=("Arial", 10, "bold"), 
            selectbackground="#40444b", 
            relief=tk.FLAT, 
            bd=0, 
            highlightthickness=0
        )
        self.user_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.user_listbox.bind("<Double-Button-1>", self.on_user_click)

        input_frame = tk.Frame(self.root, bg="#202225")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.msg_entry = tk.Entry(
            input_frame, 
            bg="#40444b", 
            fg="white", 
            insertbackground="white", 
            font=("Arial", 11)
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        file_btn = tk.Button(
            input_frame, 
            text="📎 File", 
            command=self.select_and_send_file, 
            bg="#4f545c", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            padx=10, 
            pady=3, 
            relief=tk.FLAT
        )
        file_btn.pack(side=tk.RIGHT, padx=(5, 0))

        send_btn = tk.Button(
            input_frame, 
            text="Send", 
            command=self.send_message, 
            bg="#5865f2", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            padx=15, 
            pady=3, 
            relief=tk.FLAT
        )
        send_btn.pack(side=tk.RIGHT)

    def on_user_click(self, event):
        selected_index = self.user_listbox.curselection()
        if selected_index:
            target_user = self.user_listbox.get(selected_index[0]).replace("● ", "").strip()
            if target_user != self.username:
                self.msg_entry.delete(0, tk.END)
                self.msg_entry.insert(0, f"/msg {target_user} ")
                self.msg_entry.focus()

    def display_message(self, message, tag="normal"):
        now = datetime.now().strftime("[%I:%M %p] ")
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, now, "time")
        self.chat_area.insert(tk.END, message + "\n", tag)
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def update_user_list(self, raw_names):
        self.user_listbox.delete(0, tk.END)
        names = raw_names.split(",")
        for name in names:
            clean = name.strip()
            if clean:
                self.user_listbox.insert(tk.END, f"● {clean}")

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        self.msg_entry.delete(0, tk.END)

        if msg.startswith("/msg "):
            parts = msg.split(" ", 2)
            if len(parts) >= 3:
                self.display_message(f"[WHISPER to {parts[1]}]: {parts[2]}", "whisper")
        else:
            self.display_message(f"[{self.username}]: {msg}", "self")

        try:
            self.sock.sendall(msg.encode('utf-8'))
        except:
            self.display_message("[ERROR] Failed to send message.", "server")

    def select_and_send_file(self):
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Select Recipient", "Click a user from the ONLINE USERS sidebar to send them a file.")
            return

        target_user = self.user_listbox.get(selected_index[0]).replace("● ", "").strip()
        if target_user == self.username:
            messagebox.showwarning("Invalid Target", "Cannot send files to yourself.")
            return

        filepath = filedialog.askopenfilename()
        if not filepath:
            return

        threading.Thread(target=self._upload_file_thread, args=(filepath, target_user), daemon=True).start()

    def _upload_file_thread(self, filepath, target_user):
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        header = f"__FILE__:{target_user}:{filename}:{filesize}\n".encode('utf-8')
        try:
            self.sock.sendall(header)
            with open(filepath, "rb") as f:
                while chunk := f.read(4096):
                    self.sock.sendall(chunk)
            self.display_message(f"[FILE SENT] '{filename}' ({filesize} bytes) sent to {target_user}.", "file")
        except Exception as e:
            self.display_message(f"[FILE ERROR] Upload failed: {e}", "server")

    def receive_messages(self):
        buffer = b""
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.display_message("[SERVER DISCONNECTED]", "server")
                    break

                buffer += data

                # Check for incoming file stream
                if buffer.startswith(b"__FILE__:"):
                    header_end = buffer.find(b"\n")
                    if header_end == -1:
                        continue

                    header = buffer[:header_end].decode('utf-8')
                    _, sender, filename, filesize = header.split(":")
                    filesize = int(filesize)

                    file_bytes = buffer[header_end + 1:]
                    buffer = b""

                    # Download all incoming chunks
                    while len(file_bytes) < filesize:
                        chunk = self.sock.recv(min(4096, filesize - len(file_bytes)))
                        if not chunk:
                            break
                        file_bytes += chunk

                    # Prompt recipient for save location
                    save_path = filedialog.asksaveasfilename(
                        initialfile=filename,
                        title=f"Save file from {sender}"
                    )
                    if save_path:
                        with open(save_path, "wb") as f:
                            f.write(file_bytes[:filesize])
                        self.display_message(f"[FILE SAVED] '{filename}' saved to {save_path}", "file")
                    else:
                        self.display_message(f"[FILE CANCELED] Download of '{filename}' was skipped.", "server")
                    continue

                # Standard text stream
                text = buffer.decode('utf-8', errors='ignore')
                buffer = b""

                if text.startswith("__USERS__:"):
                    self.update_user_list(text.replace("__USERS__:", ""))
                elif text.startswith("[SERVER]"):
                    self.display_message(text, "server")
                elif text.startswith("[WHISPER"):
                    self.display_message(text, "whisper")
                else:
                    self.display_message(text, "normal")

            except Exception:
                break
        self.sock.close()

    def on_close(self):
        try:
            self.sock.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()