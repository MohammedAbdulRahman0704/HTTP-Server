import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()  # Listen for incoming connections

    while True:
        client_socket, _ = server_socket.accept()  # Accept client connection
        request_data = client_socket.recv(1024).decode()  # Read request

        print("Received request:\n", request_data)  # Debugging

        # Extract the first line (Request Line)
        request_line = request_data.split("\r\n")[0]
        parts = request_line.split(" ")

        if len(parts) > 1:
            path = parts[1]  # Extract URL path
        else:
            path = "/"

        # Handle `/echo/{str}` endpoint
        if path.startswith("/echo/"):
            echo_string = path[len("/echo/"):]  # Extract the string after "/echo/"
            response_body = echo_string
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
            )
            response = response_headers + response_body

        elif path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response.encode())  # Send response
        client_socket.close()  # Close connection


if __name__ == "__main__":
    main()