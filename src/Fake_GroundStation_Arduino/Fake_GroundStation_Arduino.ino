typedef struct __attribute__((__packed__)) {
  uint8_t packetType;
  uint8_t softwareVersion;
  uint8_t board_serial_num;
  uint32_t timestampMs;
  char callsign[8];//14

  float temp, pos_z, vel_z, lat, lon, gps_alt, batt_volts, speedKnots,
        courseDeg;
  uint32_t gpsTime;
  uint8_t sats, state, btClients;

  uint8_t radio_id;
  int8_t rssi;
  bool crc;
  uint8_t lqi;
} TransmitData_t;
static TransmitData_t transmitPacket;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // Gather packet
  transmitPacket.packetType = 3;
  transmitPacket.softwareVersion = 0;
  transmitPacket.board_serial_num = 0;
  transmitPacket.timestampMs = millis();
  char *call = "KM6GNL";
  strncpy(transmitPacket.callsign, call, 8);

  transmitPacket.lat = 10.00;
  transmitPacket.lon = 11.00;
  transmitPacket.gps_alt = 20.5;
  transmitPacket.batt_volts = 12;
  transmitPacket.state = 2;
  transmitPacket.vel_z = 10;
  transmitPacket.lqi = 255;
  transmitPacket.crc = true;

  Serial.write((char*)(uint8_t*) &transmitPacket, sizeof(transmitPacket));
  delay(100);
}
