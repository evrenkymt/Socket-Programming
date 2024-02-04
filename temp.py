import socket
import time
from random import randint
import logging

GATEWAY_HOST = socket.gethostbyname(socket.gethostname())
GATEWAY_PORT = 9091

temperature_sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
temperature_sensor.connect((GATEWAY_HOST, GATEWAY_PORT))

logging.basicConfig(filename='temperature_sensor.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def send():
    while True:
        temperature_value = randint(20,30)
        time_stamp = time.time()
        print(f"temperature: {temperature_value} - timestamp: {int(time_stamp)}  sent to Gateway.")
        logging.info(f"temperature: {temperature_value} - timestamp: {int(time_stamp)}  sent to Gateway.")
        
        temperature_sensor.send(f"temperature: {temperature_value} timestamp: {int(time_stamp)}".encode('utf-8'))
        time.sleep(1)
send()