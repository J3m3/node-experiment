import socket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def handle_client_connection(client_socket, client_address):
    logging.info(f"Connection from {client_address} established.")

    # Receive the data from the client
    request = client_socket.recv(1024).decode("utf-8")
    logging.info(f"Received data from {client_address}:\n{request}")

    # Parse the request line (first line of the HTTP request)
    request_line = request.splitlines()[0]
    method, path, version = request_line.split()

    if method == "GET":
        logging.info(f"Handling GET request for {path}")

        # Crafting a basic HTTP response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += (
            "<html><body><h1>Hello! You've reached the server.</h1></body></html>"
        )

        # Send the response
        client_socket.sendall(response.encode("utf-8"))
        logging.info(f"Sent response to {client_address}")
    else:
        logging.warning(f"Unsupported method: {method}")

    # Close the client connection
    client_socket.close()
    logging.info(f"Connection with {client_address} closed.")


def run_server(host="127.0.0.1", port=8080):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Server started on {host}:{port}")

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()
            handle_client_connection(client_socket, client_address)
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user.")
    finally:
        server_socket.close()
        logging.info("Server closed.")


if __name__ == "__main__":
    run_server()
