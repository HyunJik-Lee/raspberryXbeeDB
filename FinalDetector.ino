#include <Seeed_AMG8833_driver.h>
#include <XBee.h>
#include <OneWire.h>
#include <MQ7.h>

int Buzzer = 8;
int FlameSensor = A0; //#define A0 14
int MQ7Sensor = A1;   //#define A1 15
int TempSensor = 9;
boolean isFire = false;
AMG8833 sensor;
XBee xbee = XBee();
uint8_t payload[86] = {0};
XBeeAddress64 addr64 = XBeeAddress64(0x0013a200, 0x40a8c860);
ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));
char gastmp[6];
char temptmp[6];
char flametmp[6];
int pix_arr[PIXEL_NUM] ={ 0} ;
float pixels_temp[PIXEL_NUM] = {0};

MQ7 mq7(MQ7Sensor, 5.0);
OneWire ds(TempSensor);

void setup() {
  pinMode(Buzzer, OUTPUT);
  pinMode(FlameSensor, INPUT);
  pinMode(TempSensor, INPUT);
  Serial.begin(9600);
  sensor.init();
  xbee.setSerial(Serial);
}

void loop() {
  FireDetect();
}

void FireDetect(){
  float gasValue = Gas_sensor();
  float tempValue = Temperature_sensor();
  float flameValue = Flame_sensor();
  IF_sensor();
  boolean isFire = false;
  
  dtostrf(gasValue, 6, 2, gastmp);
  dtostrf(tempValue, 6, 2, temptmp);
  dtostrf(flameValue, 6, 2, flametmp);

  payload[0] = 'G';
  for(int i = 1; i <= 6; i++){
    payload[i] = gastmp[i-1];
  }
  payload[7] = 'T';
  for(int i = 8; i<=13; i++){
    payload[i] = temptmp[i-8];
  }
  payload[14] = 'F';
  for(int i = 15; i <= 20; i++){
    payload[i] = flametmp[i-15];
  }
  payload[21] = 'e';
  for(int i = 0; i < PIXEL_NUM; i++){
    payload[22+i] = pix_arr[i];
  }

  xbee.send(zbTx);

  if(tempValue >= 60.0 || gasValue >= 30.0 || flameValue >= 130){
    isFire = true;
    playWarning();
  }
  delay(5000);
}

void IF_sensor(){
  sensor.read_pixel_temperature(pixels_temp);
  for(int i = 0; i < PIXEL_NUM; i++){
    pix_arr[i] = round(pixels_temp[i]);
    if(pix_arr[i] > 80.0)
      pix_arr[i] = 80;      
  }
  return;
}

float Gas_sensor(){
  return mq7.getPPM();
}

float Flame_sensor(){
  return getDistance();
}

float Temperature_sensor(){
  return getTemp();
}

void playWarning(){
  for(int i = 200; i <= 800; i++){
    tone(Buzzer,i);
    delay(5);
  }
  delay(2000);
  for(int i = 800; i>-200;i--){
    tone(Buzzer,i);
    delay(10);
  }
  noTone(Buzzer);
}

float getDistance(){
  return analogRead(FlameSensor);
  
}

float getTemp() {
  byte data[12];
  byte addr[8];
  if ( !ds.search(addr)) {
    ds.reset_search();
    return -1000;
  }
  if ( OneWire::crc8( addr, 7) != addr[7]) {
    Serial.println("CRC is not valid!");
    return -1000;
  }
  if ( addr[0] != 0x10 && addr[0] != 0x28) {
    Serial.print("Device is not recognized");
    return -1000;
  }
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);
  byte present = ds.reset();
  ds.select(addr);
  ds.write(0xBE);
  for (int i = 0; i < 9; i++)  {
    data[i] = ds.read();
  }
  ds.reset_search();
  byte MSB = data[1];
  byte LSB = data[0];
  float tempRead = ((MSB << 8) | LSB);
  float TemperatureSum = tempRead / 16;
  return TemperatureSum;
}
