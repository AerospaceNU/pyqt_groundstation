typedef struct __attribute__((__packed__)) {
  float  gps_lat,     gps_long,     gps_alt;
  float    baro_pres;
  double   battery_voltage;
  uint8_t  pyro_continuity;
  uint8_t  state;
} TransmitData_t;

static TransmitData_t transmitPacket;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // Gather packet
  transmitPacket.gps_lat = 10.00;
  transmitPacket.gps_long = 11.00;
  transmitPacket.gps_alt = 20.5;
  transmitPacket.baro_pres = 1000;
  transmitPacket.battery_voltage = 12;
  transmitPacket.pyro_continuity = 0;
  transmitPacket.state = 2;

  Serial.write((char*)(uint8_t*) &transmitPacket, sizeof(transmitPacket));
  Serial.println();
  delay(100);
}
