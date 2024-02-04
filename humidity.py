import socket
import random
import time
import threading
import logging

GATEWAY_HOST = socket.gethostbyname(socket.gethostname())
GATEWAY_PORT = 9090

humidity_sensor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
humidity_sensor.bind((GATEWAY_HOST, random.randint(8000,9000)))

logging.basicConfig(filename='humidity_sensor.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def humidity_value():
    while True:
        value = random.randint(40,90)
        time_stamp_1 = time.time()
        
        print(f"humidity: {value} - timestamp: {int(time_stamp_1)}")
        
        if(value > 80):
            print(f"Humidity value -{value}- exceed 80. Sent to Gateway.")
            logging.info(f"Humidity value -{value}- exceed 80. Sent to Gateway.")

            humidity_sensor.sendto(f"humidity: {value} - timestamp: {int(time_stamp_1)}".encode('utf-8'),(GATEWAY_HOST,GATEWAY_PORT))
        time.sleep(1)

def alive_message():
    while True:        
        time_stamp_2 = time.time()
        print(f"ALIVE message sent to Gateway at {int(time_stamp_2)}")
        logging.info(f"ALIVE message sent to Gateway. at {int(time_stamp_2)}")
        
        humidity_sensor.sendto(f"ALIVE - timestamp:{int(time_stamp_2)}".encode('utf-8'),(GATEWAY_HOST,GATEWAY_PORT))
        time.sleep(3)

humidity_value_thread = threading.Thread(target=humidity_value)
alive_message_thread = threading.Thread(target=alive_message)

humidity_value_thread.start()
alive_message_thread.start()

humidity_value_thread.join()
alive_message_thread.join()