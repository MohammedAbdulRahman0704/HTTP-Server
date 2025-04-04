import socket
import threading
import os
import sys

# Global variable for directory
FILES_DIRECTORY = ""


def handle_client(client_socket):
    """Handles an individual client connection."""
    request_data = client_socket.recv(1024).decode()  # Read request
    print("Received request:\n", request_data)  # Debugging

    # Split request into lines
    lines = request_data.split("\r\n")

    # Extract request line (first line)
    request_line = lines[0]
    parts = request_line.split(" ")

    if len(parts) > 1:
        path = parts[1]  # Extract URL path
    else:
        path = "/"

    # Extract headers into a dictionary
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key] = value

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

    # Handle `/user-agent` endpoint
    elif path == "/user-agent":
        user_agent = headers.get("User-Agent", "")  # Get User-Agent or empty string
        response_body = user_agent
        response_headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
        )
        response = response_headers + response_body

    # Handle `/files/{filename}` endpoint
    elif path.startswith("/files/"):
        filename = path[len("/files/"):]  # Extract filename
        file_path = os.path.join(FILES_DIRECTORY, filename)

        if os.path.isfile(file_path):  # Check if file exists
            with open(file_path, "rb") as file:
                file_content = file.read()

            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                "\r\n"
            )
            client_socket.sendall(response_headers.encode() + file_content)
            client_socket.close()
            return
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

    # Handle root `/`
    elif path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"

    # Handle unknown paths
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"

    client_socket.sendall(response.encode())  # Send response
    client_socket.close()  # Close connection


def main():
    global FILES_DIRECTORY

    # Parse command-line arguments
    if "--directory" in sys.argv:
        dir_index = sys.argv.index("--directory") + 1
        if dir_index < len(sys.argv):
            FILES_DIRECTORY = sys.argv[dir_index]
        else:
            print("Error: --directory flag requires a path")
            sys.exit(1)
    else:
        print("Error: --directory flag is required")
        sys.exit(1)

    print(f"Serving files from: {FILES_DIRECTORY}")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()  # Listen for incoming connections

    while True:
        client_socket, _ = server_socket.accept()  # Accept client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()  # Start a new thread for each client


if __name__ == "__main__":
    main()