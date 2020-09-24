import RPi.GPIO
import serial
import time
from xbee import XBee
import mariadb
from datetime import datetime
import json
from calc import cal
try:
    conn = mariadb.connect(
            user="root",
            password="21511785",
            host="165.229.89.54",
            port=3306,
            database="sensor"
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
if_arr = []
if_json = ""

def receive_data(data):
    gas_buf = ""
    tmp_buf = ""
    flame_buf = ""
    GAS = 0.0
    TEMP = 0.0
    FLAME = 0.0
    x = 0
    if_arr = []
    if_json = ""
    #print("data:{}".format(data['rf_data']))
    data_arr = list(data['rf_data'])
    print(data_arr)
    if_arr = data_arr[22:]
    if_json = json.dumps(if_arr)
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
    cur.execute('select sense_gas, sense_temp from sensitivity order by sense_id desc limit 1')
    gas_sen, temp_sen = cur.fetchone()
    percent, step = cal(GAS, TEMP, FLAME, gas_sen, temp_sen)
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('insert into probability(percent, step, date) values (%s, %s, %s)', (percent, step, date))
    cur.execute('insert into sensor(GAS, TEMP, FLAME, DATE, IFCAM) values (%s, %s, %s, %s, %s)', (GAS, TEMP, FLAME, date, if_json))
    print(GAS)
    print(TEMP)
    print(FLAME)
    print(if_json)

ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE)
xbee= XBee(ser, callback = receive_data, escaped=True)

while True:
    try:
        time.sleep(0.001)
    except KeyboardInterrupt:
        break

xbee.halt()
ser.close()
