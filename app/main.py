import socket
import threading
import sys

def main():
    def handle_req(client, addr):
        data = client.recv(1024)
        req = data.decode().split("\r\n")

        if not req or len(req[0].split(" ")) < 2:
            client.close()
            return

        method, path = req[0].split(" ")[0], req[0].split(" ")[1]
        headers = {}
        body = b""

        # Parse headers
        i = 1
        while req[i]:
            key, value = req[i].split(": ", 1)
            headers[key] = value
            i += 1

        # Read body if POST
        content_length = int(headers.get("Content-Length", 0))
        header_bytes_len = len("\r\n".join(req[:i + 1])) + 2
        body = data[header_bytes_len:]
        while len(body) < content_length:
            body += client.recv(1024)

        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n".encode()

        elif path.startswith("/echo"):
            content = path[6:]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}".encode()

        elif path.startswith("/user-agent"):
            user_agent = headers.get("User-Agent", "")
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()

        elif path.startswith("/files"):
            directory = sys.argv[2]  # --directory path
            filename = path[7:]
            file_path = f"{directory}/{filename}"

            if method == "GET":
                try:
                    with open(file_path, "r") as f:
                        body_content = f.read()
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body_content)}\r\n\r\n{body_content}".encode()
                except Exception:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

            elif method == "POST":
                try:
                    with open(file_path, "wb") as f:
                        f.write(body)
                    response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                except Exception:
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()

            else:
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

        client.send(response)
        client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()