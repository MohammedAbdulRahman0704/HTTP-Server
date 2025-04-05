import socket
import threading
import sys
import os

def main():
    if "--directory" not in sys.argv:
        print("Usage: python3 your_program.py --directory <path>")
        sys.exit(1)

    dir_index = sys.argv.index("--directory") + 1
    if dir_index >= len(sys.argv):
        print("Error: --directory flag provided but no path")
        sys.exit(1)

    directory = sys.argv[dir_index]

    def handle_req(client, addr):
        data = client.recv(1024 * 1024).decode()
        if not data:
            client.close()
            return

        req = data.split("\r\n")
        request_line = req[0]
        headers = {}
        i = 1
        while req[i] != "":
            if ": " in req[i]:
                key, value = req[i].split(": ", 1)
                headers[key.lower()] = value
            i += 1

        method, path, _ = request_line.split(" ")
        body = "\r\n".join(req[i+1:])

        response = ""

        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            message = path[6:]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(message)}\r\n\r\n{message}"
        elif path.startswith("/user-agent"):
            user_agent = headers.get("user-agent", "")
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
        elif path.startswith("/files/"):
            filename = path[7:]
            file_path = os.path.join(directory, filename)

            if method == "GET":
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n{content}"
                except FileNotFoundError:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

            elif method == "POST":
                content_length = int(headers.get("content-length", 0))
                body_data = data.split("\r\n\r\n", 1)[1]
                # If body not fully received yet, receive rest
                while len(body_data) < content_length:
                    body_data += client.recv(1024).decode()

                try:
                    with open(file_path, "w") as f:
                        f.write(body_data)
                    response = "HTTP/1.1 201 Created\r\n\r\n"
                except Exception as e:
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client.sendall(response.encode())
        client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()


if __name__ == "__main__":
    main()