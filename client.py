import socket
import threading
import sys

HOST = '10.111.221.55'  # Replace with your actual IPv4 address
PORT = 65432

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[SERVER DISCONNECTED]")
                break
            print(f"\n{message}")
            print("> ", end="", flush=True)
        except:
            break
    client_socket.close()
    sys.exit()

def send_messages(client_socket):
    while True:
        try:
            text = input("> ")
            if text.strip().lower() == "exit":
                break
            if text.strip():
                client_socket.sendall(text.encode('utf-8'))
        except (KeyboardInterrupt, EOFError):
            break
    client_socket.close()
    sys.exit()

def start_client():
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    # Handshake step: Send username immediately after connecting
    client.sendall(username.encode('utf-8'))

    print(f"[CONNECTED] Joined chat. Commands:\n - Type normally to broadcast\n - /msg <user> <text> for private message\n - 'exit' to quit\n")

    recv_thread = threading.Thread(target=receive_messages, args=(client,))
    recv_thread.daemon = True
    recv_thread.start()

    send_messages(client)

if __name__ == "__main__":
    start_client()