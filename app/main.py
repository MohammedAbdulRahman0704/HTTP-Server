import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()  # Listen for incoming connections

    while True:
        client_socket, _ = server_socket.accept()  # Accept client connection
        request_data = client_socket.recv(1024).decode()  # Read request

        print("Received request:\n", request_data)  # Debugging

        # HTTP 200 OK response
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "Hello, world!"
        )

        client_socket.sendall(response.encode())  # Send response
        client_socket.close()  # Close connection


if __name__ == "__main__":
    main()