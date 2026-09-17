import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 65432

clients = {}  # {client_socket: username}

def broadcast(message, sender_socket=None):
    for sock in list(clients.keys()):
        if sock != sender_socket:
            try:
                sock.sendall(message)
            except:
                cleanup_client(sock)

def send_user_list():
    users_msg = f"__USERS__:{','.join(clients.values())}".encode('utf-8')
    broadcast(users_msg)

def cleanup_client(sock):
    if sock in clients:
        name = clients[sock]
        del clients[sock]
        try:
            sock.close()
        except:
            pass
        print(f"[DISCONNECTED] {name} left.")
        broadcast(f"[SERVER] {name} has left the chat.".encode('utf-8'))
        send_user_list()

def handle_client(sock, addr):
    try:
        username = sock.recv(1024).decode('utf-8').strip()
        if not username:
            return
        clients[sock] = username
        print(f"[REGISTERED] {addr} as '{username}'")
        
        broadcast(f"[SERVER] {username} joined the chat!".encode('utf-8'), sock)
        send_user_list()

        while True:
            raw = sock.recv(4096)
            if not raw:
                break

            # Handle file routing: __FILE__:<target>:<filename>:<filesize>
            if raw.startswith(b"__FILE__:"):
                header = raw.decode('utf-8', errors='ignore')
                parts = header.split(":", 3)
                target_user = parts[1]
                filename = parts[2]
                filesize = int(parts[3])

                target_sock = None
                for s, name in clients.items():
                    if name.lower() == target_user.lower():
                        target_sock = s
                        break

                if target_sock:
                    # Forward header to recipient
                    target_sock.sendall(f"__FILE__:{username}:{filename}:{filesize}".encode('utf-8'))
                    
                    # Relay the raw file bytes
                    remaining = filesize
                    while remaining > 0:
                        chunk = sock.recv(min(remaining, 4096))
                        if not chunk:
                            break
                        target_sock.sendall(chunk)
                        remaining -= len(chunk)
                continue

            # Standard chat/whisper
            text = raw.decode('utf-8', errors='ignore').strip()
            if text.startswith("/msg "):
                parts = text.split(" ", 2)
                if len(parts) >= 3:
                    target_user, msg_content = parts[1], parts[2]
                    for s, name in clients.items():
                        if name.lower() == target_user.lower():
                            s.sendall(f"[WHISPER from {username}]: {msg_content}".encode('utf-8'))
                            sock.sendall(f"[WHISPER to {target_user}]: {msg_content}".encode('utf-8'))
                            break
            else:
                broadcast(f"[{username}]: {text}".encode('utf-8'), sock)

    except Exception as e:
        print(f"[CLIENT ERROR] {e}")
    finally:
        cleanup_client(sock)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[RUNNING] Server listening on {HOST}:{PORT}")

    while True:
        client_sock, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()

if __name__ == "__main__":
    start_server()