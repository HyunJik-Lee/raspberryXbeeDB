import RPi.GPIO
import serial
import time
from xbee import XBee
import mysql.connector
from datetime import datetime

try:
    conn = mariadb.connect(
            user="jiggy0429",
            password="python21511785",
            host="jiggy0429.mysql.pythonanywhere-services.com",
            port=3306,
            database="jiggy0429$default"
            )
except mariadb.Error as e:
    print(f"DB 연결 오류 : {e}")

cur = conn.cursor()

SERIAL_PORT="/dev/ttyUSB0"
BAUD_RATE = 9600
data_arr = []
gas_buf = ""
tmp_buf = ""
flame_buf = ""
GAS = 0.0
TEMP = 0.0
FLAME = 0.0
x = 0

def receive_data(data):
    gas_buf = ""
    tmp_buf = ""
    flame_buf = ""
    GAS = 0.0
    TEMP = 0.0
    FLAME = 0.0
    x = 0
    #print("data:{}".format(data['rf_data']))
    data_arr = list(data['rf_data'])
    #print(data_arr)
    while x != len(data_arr):
      if data_arr[x] == 71:
        x+= 2
        while data_arr[x] != 84:
          gas_buf += chr(data_arr[x])
          x += 1
        GAS = float(gas_buf) 
      if data_arr[x] == 84:
        x+=2
        while data_arr[x] != 70:
          tmp_buf += chr(data_arr[x])
          x+=1
        TEMP = float(tmp_buf)
      if data_arr[x] == 70:
        x+=2
        while data_arr[x] != 101:
          flame_buf += chr(data_arr[x])
          x+=1
        FLAME = float(flame_buf)
      x+=1

    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('insert into sensor(GAS, TEMP, FLAME, DATE) values (%s, %s, %s, %s)', (GAS, TEMP, FLAME, date))
    print(GAS)
    print(TEMP)
    print(FLAME)
    

ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE)
xbee= XBee(ser, callback = receive_data, escaped=True)

while True:
    try:
        time.sleep(0.001)
    except KeyboardInterrupt:
        break

xbee.halt()
ser.close()
