#include <EEPROM.h>

#define LDACPIN_LOW  ( PORTB &= B11111011 ) // pin 10
#define LDACPIN_HIGH ( PORTB |= B00000100 )
#define SDIPIN_LOW   ( PORTB &= B11110111 ) // pin 11
#define SDIPIN_HIGH  ( PORTB |= B00001000 )
#define SCKPIN_LOW   ( PORTB &= B11101111 ) // pin 12
#define SCKPIN_HIGH  ( PORTB |= B00010000 )
#define CSPIN_LOW    ( PORTB &= B11111101 ) // pin 9
#define CSPIN_HIGH   ( PORTB |= B00000010 )

#define CLOCK        SCKPIN_HIGH; SCKPIN_LOW;
#define SET_HIGH     SDIPIN_HIGH; CLOCK;
#define SET_LOW      SDIPIN_LOW;  CLOCK;

#define INLENGTH 128
#define INTERMINATOR 13
#define TABLELENGTH 48

/*
const int sensorPin = A0;
const int latchPin = 5;
const int clockPin = 3;
const int dataPin = 4;
const int ledPin = 13;
const int resetPin = 6;
*/

// Calibration values
float max_voltage; //= 6;
float min_voltage; //= -6;

boolean led = true; // LED on or off

boolean sweeping = false;
int nsweep_points;
int sweep_values[TABLELENGTH];
int sweep_delays[TABLELENGTH];

void set_dac_2 ( int value_a, int value_b ){

  // --- output A ---
  CSPIN_LOW;

  SDIPIN_HIGH; CLOCK; // 15
  SDIPIN_LOW;  CLOCK; // 14
  SDIPIN_HIGH; CLOCK; // 13
  CLOCK;              // 12
  
  SDIPIN_LOW;  if ( 2048 & value_a ){ SDIPIN_HIGH; } CLOCK; // 11
  SDIPIN_LOW;  if ( 1024 & value_a ){ SDIPIN_HIGH; } CLOCK; // 10
  SDIPIN_LOW;  if (  512 & value_a ){ SDIPIN_HIGH; } CLOCK; // 09
  SDIPIN_LOW;  if (  256 & value_a ){ SDIPIN_HIGH; } CLOCK; // 08
  SDIPIN_LOW;  if (  128 & value_a ){ SDIPIN_HIGH; } CLOCK; // 07
  SDIPIN_LOW;  if (   64 & value_a ){ SDIPIN_HIGH; } CLOCK; // 06
  SDIPIN_LOW;  if (   32 & value_a ){ SDIPIN_HIGH; } CLOCK; // 05
  SDIPIN_LOW;  if (   16 & value_a ){ SDIPIN_HIGH; } CLOCK; // 04
  SDIPIN_LOW;  if (    8 & value_a ){ SDIPIN_HIGH; } CLOCK; // 03
  SDIPIN_LOW;  if (    4 & value_a ){ SDIPIN_HIGH; } CLOCK; // 02
  SDIPIN_LOW;  if (    2 & value_a ){ SDIPIN_HIGH; } CLOCK; // 01
  SDIPIN_LOW;  if (    1 & value_a ){ SDIPIN_HIGH; } CLOCK; // 00

  CSPIN_HIGH;

  // --- output B ---
  CSPIN_LOW;

  SDIPIN_LOW; CLOCK;  // 15
  CLOCK;              // 14
  SDIPIN_HIGH; CLOCK; // 13
  CLOCK;              // 12

  SDIPIN_LOW;  if ( 2048 & value_b ){ SDIPIN_HIGH; } CLOCK; // 11
  SDIPIN_LOW;  if ( 1024 & value_b ){ SDIPIN_HIGH; } CLOCK; // 10
  SDIPIN_LOW;  if (  512 & value_b ){ SDIPIN_HIGH; } CLOCK; // 09
  SDIPIN_LOW;  if (  256 & value_b ){ SDIPIN_HIGH; } CLOCK; // 08
  SDIPIN_LOW;  if (  128 & value_b ){ SDIPIN_HIGH; } CLOCK; // 07
  SDIPIN_LOW;  if (   64 & value_b ){ SDIPIN_HIGH; } CLOCK; // 06
  SDIPIN_LOW;  if (   32 & value_b ){ SDIPIN_HIGH; } CLOCK; // 05
  SDIPIN_LOW;  if (   16 & value_b ){ SDIPIN_HIGH; } CLOCK; // 04
  SDIPIN_LOW;  if (    8 & value_b ){ SDIPIN_HIGH; } CLOCK; // 03
  SDIPIN_LOW;  if (    4 & value_b ){ SDIPIN_HIGH; } CLOCK; // 02
  SDIPIN_LOW;  if (    2 & value_b ){ SDIPIN_HIGH; } CLOCK; // 01
  SDIPIN_LOW;  if (    1 & value_b ){ SDIPIN_HIGH; } CLOCK; // 00

  CSPIN_HIGH;

  LDACPIN_LOW;
  SCKPIN_HIGH;
  LDACPIN_HIGH;
  SCKPIN_LOW;

}

int voltageToDAC(float voltage){
  // Converts a voltage as a float to ADC units
  int dac = int( (voltage - min_voltage) / ((max_voltage-min_voltage)/4096) );
  return dac;
}

float DACtovoltage(int dac){
  // Converts DAC units to voltage
  float voltage = float(dac * ((max_voltage-min_voltage)/4096) + min_voltage);
  return voltage;
}

void float_to_eeprom(float f, int address){
  // Saves a float f into 4 bytes of EEPROM starting at given address
  union u_tag {
    byte b[4];
    float fval;
  } u;
 
  u.fval=f;
  int i = 0;
  for (i=0; i<4; i++) {
    //Serial.print("At "); Serial.println(i);
    //Serial.print("Saving "); Serial.println(byte(u.b[i])); 
    EEPROM.write(address+i, u.b[i]);
  }
}

float float_from_eeprom(int address){
 // Returns a float from 4 bytes of eeprom starting at given address
 union u_tag {
    byte b[4];
    float fval;
  } u;
  
  for (int i=0; i<4; i++)
    u.b[i] = EEPROM.read(address+i);
  float f = u.fval;
  return f;
}

char* readString(){
  // Reads a character string from the serial terminal
  // Note, returns a static char array, so you can't be sure it will point to
  // the same thing after multiple calls.
  static char inString[INLENGTH+1];
  int inCount = 0;
  do {
    while (!Serial.available());             // wait for input
    inString[inCount] = Serial.read();       // get it
    Serial.print(inString[inCount]);
    if (inString [inCount] == INTERMINATOR) break;
  } while (++inCount < INLENGTH);
  inString[inCount] = 0;                     // null terminate the string
  Serial.println("");
  //Serial.print("Read : ");
  //Serial.println(inString);
  return inString;
}

void setVoltage() {
  char* command = readString();
  float v = atof( command );
  if( v < 0. || v > 1.5 )
    return;
  set_dac_2( voltageToDAC(v), voltageToDAC(v) );
  sweeping = false;
}

void setSweep() {
 char* command = readString();
 nsweep_points = atoi( command );
 if( nsweep_points > TABLELENGTH )
  nsweep_points = TABLELENGTH;
  
 for( int i = 0; i < nsweep_points; ++i ) {
   command = readString();
   float v = atof( command );
   if( v < 0. || v > 1.5 )
    v = 0.;
    
   sweep_values[i] = voltageToDAC( v );
   command = readString();
   sweep_delays[i] = atoi( command );
 } 
 sweeping = true;
}

void parseCommand() {
 if( Serial.available() > 0 ) {
   char b = Serial.read();
   switch( b ) {
    case 'v':
     setVoltage();
     break;
    case 's':
     setSweep();
     break;
    default:
     Serial.println( "Command not recognized. Available commands:" );
     Serial.println( "v - set voltage" );
     Serial.println( "s - set sweep" );
     break;     
   }
 }
}

void setup(){
  // Setup for driving the DAC
  DDRB = DDRB | B11111111;
  
  CSPIN_HIGH;
  SCKPIN_LOW;
  SDIPIN_LOW;
  LDACPIN_HIGH;
  
  pinMode(7, OUTPUT); digitalWrite(7, LOW);
  pinMode(8, OUTPUT); digitalWrite(8, LOW);
  pinMode(2, OUTPUT); digitalWrite(2, LOW);
  pinMode(6, OUTPUT); digitalWrite(6, LOW);
  
  pinMode(13, OUTPUT); digitalWrite(13, LOW);
  pinMode(5, OUTPUT); digitalWrite(5, LOW);
  pinMode(4, OUTPUT); digitalWrite(4, LOW);
  pinMode(3, OUTPUT); digitalWrite(3, LOW);
  
  // Setup the digital pins
  //pinMode(ledPin, OUTPUT); 
  //pinMode(latchPin, OUTPUT);
  //pinMode(clockPin, OUTPUT);
  //pinMode(dataPin, OUTPUT);
  //pinMode(resetPin, OUTPUT);
  //digitalWrite(resetPin, HIGH);
  
  // Load cal values from eeprom
  min_voltage = 0.;//float_from_eeprom(0);
  max_voltage = 5.;//float_from_eeprom(4);
  
  set_dac_2( voltageToDAC( 0. ), voltageToDAC( 0. ) );

  // Setup serial comms
  Serial.begin(9600);
}

void sweep() {
  for( int i = 0; i < nsweep_points; ++i ) {
    set_dac_2( sweep_values[i], sweep_values[i] );
    delay( sweep_delays[i] );
  }
}

void loop() {
  if( sweeping )
   sweep();
  parseCommand();
}

