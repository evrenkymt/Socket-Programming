import socket
import threading
import time
import logging

GATEWAY_HOST = socket.gethostbyname(socket.gethostname())
GATEWAY_UDP_PORT = 9090
GATEWAY_TCP_PORT = 9091

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9092

gateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gateway_socket.connect((SERVER_HOST, SERVER_PORT))

logging.basicConfig(filename='gateway.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def handshake(gateway_socket):
    response = gateway_socket.recv(1024).decode('utf-8')
    if response == "HELLO":
        gateway_socket.sendall("READY".encode('utf-8'))
        return True
    else:
        return False

if handshake(gateway_socket):
    print("Handshake successfull.")
    logging.info("Handshake successfull.")
else:
    print("Handshake failed.")
    logging.info("Handshake failed.")

def humidity_udp():

    humidity_sensor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    humidity_sensor.bind((GATEWAY_HOST, GATEWAY_UDP_PORT))
    humidity_sensor.settimeout(7)
    print(f"Listening Humidity Sensor on {GATEWAY_HOST} PORT: {GATEWAY_UDP_PORT}")
    logging.info(f"Listening Humidity Sensor on {GATEWAY_HOST} PORT: {GATEWAY_UDP_PORT}")
    
    connection_established = False
    
    def receive():
        nonlocal connection_established       
        while True:
            try:
                message, addr = humidity_sensor.recvfrom(1024)
                
                if not connection_established:
                    print(f"Connected with humidity sensor on {str(addr)}")
                    logging.info(f"Connected with humidity sensor on {str(addr)}")
                    
                    connection_established = True
            
                if message:
                    print(f"Received data from humidity sensor: {message.decode()}")
                    logging.info(f"Received data from humidity sensor: {message.decode()}")
                    print(f"Sent humidity sensor data to server: {message.decode()}")
                    logging.info(f"Sent humidity sensor data to server: {message.decode()}")
                    
                    gateway_socket.sendall(message)
            except:
                current_time = int(time.time())
                print(f"Humidity sensor lost connection at {current_time}. HUMIDITY SENSOR OFF message sent to server.")
                logging.info(f"Humidity sensor lost connection at {current_time}. HUMIDITY SENSOR OFF message sent to server.")
                warning = f"HUMIDITY SENSOR OFF at {current_time}"
                gateway_socket.sendall(warning.encode())
                humidity_sensor.close()
                break
    receive()

def temperature_tcp():

    temperature_sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temperature_sensor.bind((GATEWAY_HOST, GATEWAY_TCP_PORT))
    temperature_sensor.listen()
    print(f"Listening Temperature sensor on {GATEWAY_HOST} PORT: {GATEWAY_TCP_PORT}")
    logging.info(f"Listening Temperature sensor on {GATEWAY_HOST} PORT: {GATEWAY_TCP_PORT}")
        
    def handle(sensor):    
        while True:
            message = sensor.recv(1024).decode('utf-8')
            if message:
                print(f"Received data from temperature sensor: {message}")
                logging.info(f"Received data from temperature sensor: {message}")
                print(f"Sent temperature sensor data to server: {message}")
                logging.info(f"Sent temperature sensor data to server: {message}")
                
                gateway_socket.sendall(message.encode('utf-8'))
                last_time = int(time.time())
            else:
                crrnt_time = int(time.time())
                if crrnt_time - last_time >=3:
                    crrnt_time = int(time.time())
                    print(f"Temperature sensor lost connection at {crrnt_time}. TEMP SENSOR OFF message sent to server.")
                    logging.info(f"Temperature sensor lost connection at {crrnt_time}. TEMP SENSOR OFF message sent to server.")
                    
                    warning = f"TEMP SENSOR OFF at {crrnt_time}"
                    gateway_socket.sendall(warning.encode('utf-8'))
                    sensor.close()
                    break

    def receive():
        while True:
            sensor, address = temperature_sensor.accept()
            print(f"Connected with temperature sensor on{str(address)}")
            logging.info(f"Connected with temperature sensor on{str(address)}")
            
            handle(sensor)
    receive()

temperature_thread_2 = threading.Thread(target=temperature_tcp)
humidity_thread = threading.Thread(target=humidity_udp)

temperature_thread_2.start()
humidity_thread.start()

temperature_thread_2.join()
humidity_thread.join()