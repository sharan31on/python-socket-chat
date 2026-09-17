# Cross-Platform TCP Socket Chat & File Transfer System

A high-performance local area network (LAN) chat and binary file-sharing suite built with Python TCP sockets, multi-threading, and Tkinter.

---

## 🌟 Key Features

- **Cross-Platform Communication:** Concurrent connections across Windows PCs and Android devices (via Pydroid 3).
- **Dynamic User Presence:** Real-time online member updates via a custom `__USERS__:` protocol payload.
- **Private Whispering:** Direct messaging routed with `/msg <username> <message>`.
- **Binary File Streaming:** Chunked byte transmission (`__FILE__:` framing) supporting photos, documents, and archives without interrupting the chat stream.
- **Save As Dialog:** Built-in recipient prompt to select custom download directories.
- **Modern Dark UI:** Tkinter interface with scrollable message logs, dynamic sidebar rosters, and color-coded timestamps.
- **Standalone Binary:** Packaged with PyInstaller into an autonomous Windows `.exe` requiring zero external dependencies.

---

## 📁 Repository Structure

```text
├── server.py        # Central relay server handling socket demux, presence, and file streams
├── gui_v2.py        # Tkinter desktop GUI client
├── client.py        # CLI client for Android (Pydroid 3)
├── README.md        # Technical documentation
└── dist/
    └── gui_v2.exe   # Standalone Windows executable