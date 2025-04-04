import socket
import threading
import os
import sys

# Global variable to hold directory path
FILES_DIR = None


def handle_client(client_socket):
    request_data = client_socket.recv(1024).decode()
    print("Received request:\n", request_data)

    lines = request_data.split("\r\n")
    if len(lines) == 0:
        client_socket.close()
        return

    request_line = lines[0]
    parts = request_line.split(" ")

    if len(parts) < 2:
        client_socket.close()
        return

    method, path = parts[0], parts[1]

    # File serving logic
    if path.startswith("/files/"):
        filename = path[len("/files/"):]
        file_path = os.path.join(FILES_DIR, filename)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                file_contents = f.read()

            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(file_contents)}\r\n"
                "\r\n"
            )
            client_socket.sendall(response_headers.encode() + file_contents)
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            client_socket.sendall(response.encode())

        client_socket.close()
        return

    # Handle other endpoints if required (like `/echo/`, `/user-agent/`)

    # Unknown path fallback
    response = "HTTP/1.1 404 Not Found\r\n\r\n"
    client_socket.sendall(response.encode())
    client_socket.close()


def main():
    global FILES_DIR

    print("Logs from your program will appear here!")

    # Parse --directory argument
    if "--directory" in sys.argv:
        dir_index = sys.argv.index("--directory") + 1
        if dir_index < len(sys.argv):
            FILES_DIR = sys.argv[dir_index]
        else:
            print("Error: --directory flag provided but no path given")
            sys.exit(1)
    else:
        print("Error: --directory flag is required")
        sys.exit(1)

    print(f"Serving files from: {FILES_DIR}")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    main()