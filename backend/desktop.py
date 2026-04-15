"""Desktop launcher - opens the app in a native window."""

import sys
import os
import threading
import socket

# Ensure bundled modules are importable
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)

import uvicorn
import webview
from main import app


def find_free_port():
    """Find a free port to avoid conflicts."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    port = find_free_port()

    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    webview.create_window(
        "送货单生成系统",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        min_size=(900, 600),
    )
    webview.start()
