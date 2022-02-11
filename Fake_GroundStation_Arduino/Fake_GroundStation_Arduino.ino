typedef struct __attribute__((__packed__)) {
  uint8_t packetType;
  uint8_t softwareVersion;
  uint32_t timestampMs;
  char callsign[8];//14

  float  gps_lat,     gps_long,     gps_alt;//26
  float pos_z, vel_z;//34
  float    baro_pres;//38
  double   battery_voltage;//46
  uint8_t  pyro_continuity;
  uint8_t  state;//48
  uint8_t rssi;
  uint8_t crc_lqi;
} TransmitData_t;
static TransmitData_t transmitPacket;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // Gather packet
  transmitPacket.packetType = 2;
  transmitPacket.softwareVersion = 0;
  transmitPacket.timestampMs = millis();
  char *call = "KM6GNL";
  strncpy(transmitPacket.callsign, call, 8);

  transmitPacket.gps_lat = 10.00;
  transmitPacket.gps_long = 11.00;
  transmitPacket.gps_alt = 20.5;
  transmitPacket.baro_pres = 1000;
  transmitPacket.battery_voltage = 12;
  transmitPacket.pyro_continuity = 0;
  transmitPacket.state = 2;
  transmitPacket.pos_z = 0;
  transmitPacket.vel_z = 10;
  transmitPacket.crc_lqi = 255;

  Serial.write((char*)(uint8_t*) &transmitPacket, sizeof(transmitPacket));
  delay(100);
}
