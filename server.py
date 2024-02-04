import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9092
HTTP_PORT = 8080

temperature_data = []
humidity_data = []

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def http_server():
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/temperature":
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>Temperature</title></head>", "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<h1>Temperature</h1>", "utf-8"))
                self.wfile.write(bytes("<ul>", "utf-8"))
                
                for temperature in temperature_data:
                    self.wfile.write(bytes("<li>", "utf-8"))
                    self.wfile.write(bytes(f"{temperature}", "utf-8"))
                    self.wfile.write(bytes("</li>", "utf-8"))
                self.wfile.write(bytes("</ul>", "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
                self.wfile.close()
            elif self.path == "/humidity":
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>Humidity</title></head>", "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<h1>Humidity</h1>", "utf-8"))
                self.wfile.write(bytes("<ul>", "utf-8"))

                for humidity in humidity_data:
                    self.wfile.write(bytes("<li>", "utf-8"))
                    self.wfile.write(bytes(f"{humidity}", "utf-8"))
                    self.wfile.write(bytes("</li>", "utf-8"))
                self.wfile.write(bytes("</ul>", "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
                self.wfile.close()
    httpd = HTTPServer((SERVER_HOST, HTTP_PORT), RequestHandler)
    httpd.serve_forever()


def perform_handskahe(gateway_socket):
    gateway_socket.sendall("HELLO".encode('utf-8'))
    response = gateway_socket.recv(1024).decode('utf-8')
    if response == "READY":
        return True
    else:
        return False


def handle_gateway(gateway_socket):
    if perform_handskahe(gateway_socket):
        print("Handshake successfull")
        logging.info("Handshake successfull")
        
        while True:
            data = gateway_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received data from Gateway: {data}")
            logging.info(f"Received data from Gateway: {data}")
            if data.startswith("temperature") or data.startswith("TEMP"):
                temperature_data.append(data)
            elif data.startswith("humidity") or data.startswith("HUM"):
                humidity_data.append(data)
        print("Gateway disconnected")
        logging.info("Gateway disconnected")
        
        gateway_socket.close()
    else:
        print("handshake failed.")
        logging.info("handshake failed.")

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on {SERVER_HOST}: {SERVER_PORT}")
    logging.info(f"Server listening on {SERVER_HOST}: {SERVER_PORT}")

    while True:
        gateway_socket, gateway_address = server_socket.accept()
        print(f"Accepted connection from Gateway on: {gateway_address}")
        logging.info(f"Accepted connection from Gateway on: {gateway_address}")
        handle_gateway(gateway_socket)


tcp_thread = threading.Thread(target=run_server)
http_thread = threading.Thread(target=http_server)

tcp_thread.start()
http_thread.start()

tcp_thread.join()
http_thread.join()