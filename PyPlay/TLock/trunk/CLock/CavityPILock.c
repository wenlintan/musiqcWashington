// PILock algorithm for ADuC7020 microcontroller
// Author: Matt Dietrich

#include "aduc7020.h"

// 41 MHz PLL Clock
#define CLOCK 41779200
#define MICROSECOND 42

volatile int readcontrols;
// Debug mode causes green LED to flash at the sampling frequency
//#define DEBUG_MODE 1
#define DERIV_MODE 1

enum{ NCHANNELS = 1 };
volatile unsigned long* dac[3] = { &DAC0DAT, &DAC2DAT, &DAC3DAT };
const unsigned char adc_channel = 1;
const unsigned long OUTPUT_STEP = 0x100000;

typedef struct {
	unsigned long pshift, pgain, ishift, igain, dgain;
	unsigned long lock_point, lock_min, lock_max;

	signed long integral, olderror;
	unsigned long output;
} ChannelData;

ChannelData CHANNELS[ NCHANNELS ];
const signed long INTEGRAL_LIMIT = 0xFF0000;

signed long error;
signed long error_buffer[NCHANNELS];
unsigned long total_error;

enum{ NDERIVS = 8 };
typedef struct {
	unsigned long width, value, range;
	signed long center, max_deriv;
	signed char sign;
} DerivData;

DerivData DERIVS[ NDERIVS ];

// Functions run from flash memory are slow, since it takes two clock
// cycles to read each command.  Put function in .data section for speed.
int getParams(void);
void IRQ_Handler(void);

void lockMode(int);  // __attribute__((section(".data")));
int findSlopes( signed long offset_start, signed long offset_end, signed long step, unsigned long deriv_limit );
int findSignal(void);
int scanSignal(void);
int recoverSignal(void);

int getchar (void);
int putchar(int ch);
int write(int file, unsigned char * ptr, int len);
void read_long(int file, unsigned long * ptr);

int main(void) {
	volatile int i, j;
	int restart = 1;
	long temp;
	
	// For some reason the default is to divide down the clock
	// by 8 to 5 MHz.  But I have a need... for speed!
	POWKEY1 = 0x01;
	POWCON = 0;
	POWKEY2 = 0xF4;

	// Enable IRQ for our timer
	IRQEN = WAKEUP_TIMER_BIT;

	REFCON = 1;        		// Connect internal VREF  
	ADCCP = adc_channel;	// Select ADC channel
	ADCCON = 0x0723;		// Turn on ADC, single ended read

	// Initialize DACs to use AVDD pin (use 0x12 to use VRef pin instead)
	// DACs 0, 2 and 3 control heaters, DAC1 controls error LED
	DAC0CON = DAC1CON = DAC2CON = DAC3CON = 0x12; //0x13;
	DAC0DAT = DAC1DAT = DAC2DAT = DAC3DAT = 0;
	
	GP0DAT = 0x00000000;	// P0.5 activates feedback lock
	GP4DAT = 0x04040000;	// LED Pin output enabled
	
	// Setup tx & rx pins on P1.0 and P1.1
	GP1CON = 0x011;
	
	// Start setting up UART at 9600bps
	COMIEN0 = 0;
   	COMCON0 = 0x080;					// Setting DLAB
   	COMDIV0 = 0x044;  //0x088;			// Setting DIV0 and DIV1 to DL calculated
   	COMDIV1 = 0x000;
   	COMCON0 = 0x007;					// Clearing DLAB
	
	// Setup timer 2 to increment at 32168 Hz, and to count down from 3217 to
	// obtain ~10 Hz.  Creates the only IRQ, which sets a flag to reread P0.5.
	// Changed to approximately 1Hz
	T2LD = 32170;
	T2CON = (1 << 7)|(1 << 10)|(1 << 6);

	//Setup watchdog timer
	//T3LD = 65000;
	//T3CON = (1 << 7)|(1 << 5);

	for(i=0; i<500*MICROSECOND; i++);	//Wait at least 500 uS for ADC
	
	ADCCON = 0x17A4;	//0x1720;   	// Turn on ADC, single ended read, f/32 clock speed, 16 clock read time
	DAC2DAT = 0x350000;					// Set ref point dac to about 120mV / 2.5V scale

	while( 1 ) {
		write(0, (unsigned char*)"Start\r\n", 7);
		if( (temp = findSlopes( 0, 500*OUTPUT_STEP, OUTPUT_STEP, 30 )) ) {
			write(0, (unsigned char*)"Yes\r\n", 5);
			write(0, (unsigned char*)(&temp), sizeof(long));
			write(0, (unsigned char*)"\r\n", 2);
			for( j=0; j<temp; ++j ) {
				write(0, (unsigned char*)(&DERIVS[j].center), sizeof(long));
				write(0, (unsigned char*)(&DERIVS[j].value), sizeof(long));
				write(0, (unsigned char*)(&DERIVS[j].max_deriv), sizeof(long));
				write(0, (unsigned char*)"\r\n", 2);
			}
		} else {
			write(0, (unsigned char*)"No\r\n", 4);
		}

		for( j=0; j<500; ++j ) {
			*dac[0] = ( (0x7FFF0000u + j*OUTPUT_STEP) >> 4 ) & 0xFFF0000u;
			for( i=0; i<50*MICROSECOND; ++i );		// Wait a little for changes to propagate
			
			while(!ADCSTA);
			temp = (signed long)(ADCDAT >> 16);
			write(0, (unsigned char*)(&temp), sizeof(long));
			write(0, (unsigned char*)"\r\n", 2);
		}
	}
	
	for(;;) {
		GP4DAT ^= 0x00040000;
		if( getParams() ) {
			lockMode( restart );
			restart = 0;
		} else {
			while( !readcontrols );
			restart = 1;
			*dac[0] = (0x7FFF0000u>>4) & 0xFFF0000u;
		}
	}

	return 0;
}

int getchar (void)  {
	while(!(0x01==(COMSTA0 & 0x01)));
	return (COMRX);
}

int putchar(int ch)  {
	while(!(0x020==(COMSTA0 & 0x020)));
	return (COMTX = ch);
}

int write (int file, unsigned char * ptr, int len) {
	int i;
	for (i = 0; i < len; i++) putchar (*ptr++);
	return len;
}

void read_long (int file, unsigned long * ptr) {
	int j;
	for(j=0, *ptr = 0; j<sizeof(long); j++)
		*ptr |= ((unsigned long)getchar() & 0xFF) << j*8;
}

int getParams(void) {
	int i, j;
	unsigned char test;
	unsigned long nbytes;
	readcontrols = 0;
	
	if(0x01==(COMSTA0 & 0x01)) {
		test = (COMRX);
		if( test == 'b' ) {
			nbytes = sizeof(long)*6*NCHANNELS;
			write(0, (unsigned char*)"b", 1);
			write(0, (unsigned char*)(&nbytes), sizeof(long));
			for(j=0; j<NCHANNELS; ++j) {
				write(0, (unsigned char*)(&CHANNELS[j].pshift), sizeof(long));
				write(0, (unsigned char*)(&CHANNELS[j].pgain), sizeof(long));
				write(0, (unsigned char*)(&CHANNELS[j].ishift), sizeof(long));
				write(0, (unsigned char*)(&CHANNELS[j].igain), sizeof(long));
				write(0, (unsigned char*)(&CHANNELS[j].dgain), sizeof(long));
				write(0, (unsigned char*)(&CHANNELS[j].lock_point), sizeof(long));
			}			
		}

		if( test == 'c' ) {
			nbytes = 0;
			write(0, (unsigned char*)"c", 1);
			write(0, (unsigned char*)(&nbytes), sizeof(long));

			i = 0;
			while(!(0x01==(COMSTA0 & 0x01)) && ++i < 100000*MICROSECOND);
			if( i != 100000*MICROSECOND ) {
				for(j=0; j<NCHANNELS; ++j) {
					read_long(0, &CHANNELS[j].pshift);
					read_long(0, &CHANNELS[j].pgain);
					read_long(0, &CHANNELS[j].ishift);
					read_long(0, &CHANNELS[j].igain);
					read_long(0, &CHANNELS[j].dgain);
					read_long(0, &CHANNELS[j].lock_point);
				}

				nbytes = 0;
				write(0, (unsigned char*)"d", 1);
				write(0, (unsigned char*)(&nbytes), sizeof(long));
			}
		}
	}
	
	nbytes = sizeof(long)*3*NCHANNELS;
	write(0, (unsigned char*)"a", 1);
	write(0, (unsigned char*)(&nbytes), sizeof(long));
	for(j=0; j<NCHANNELS; ++j) {
		write(0, (unsigned char*)(&CHANNELS[j].olderror), sizeof(long));
		write(0, (unsigned char*)(&CHANNELS[j].output), sizeof(long));
		write(0, (unsigned char*)(&CHANNELS[j].integral), sizeof(long));
	}
	
	// P0.5 Is the digital in to activate lock
	//return GP0DAT&(1 << 5);
	return 1;
}

void lockMode(int restart) {
	signed long delta;
	volatile int i, j;

	if( restart ) {
		scanSignal();
		CHANNELS[0].integral = 0;
	}

	while(!readcontrols) {
#ifdef DEBUG_MODE
		GP4DAT ^= 0x00040000;	// For testing sampling rate
#endif

		total_error = 0;
		for(j=0; j<NCHANNELS; ++j) {
			error = error_buffer[j];
			if(error<0)		total_error += (-error);
			else			total_error += error;
			CHANNELS[j].integral += error;
			
			if(CHANNELS[j].integral < -INTEGRAL_LIMIT)		CHANNELS[j].integral = -INTEGRAL_LIMIT;
			else if(CHANNELS[j].integral > INTEGRAL_LIMIT) 	CHANNELS[j].integral = INTEGRAL_LIMIT;

			// By reducing error here, being multiplied by pgain, we can limit the smallest
			// error that pgain sees.  This is useful for eliminating the multiplication
			// of noise usually endemic to pgain.
			delta = CHANNELS[j].pgain*(error >> CHANNELS[j].pshift) + 
					CHANNELS[j].igain*(CHANNELS[j].integral >> CHANNELS[j].ishift);
#ifdef DERIV_MODE
			delta += CHANNELS[j].dgain*(error - CHANNELS[j].olderror);
			CHANNELS[j].olderror = error;
#endif

			if(delta > 0 && delta > 0xFFFF0000u-CHANNELS[j].output )	CHANNELS[j].output = 0xFFFF0000u;
			else if(delta < 0 && (-delta) > CHANNELS[j].output )		CHANNELS[j].output = 0;
			else														CHANNELS[j].output += delta;

			// Output the upper 12 bits of output
			// Lower bits represent fractions of a single output level
			*dac[j] = (CHANNELS[j].output>>4) & 0xFFF0000;

			while(!ADCSTA);
			error_buffer[j] = (signed long)(ADCDAT >> 16) - CHANNELS[j].lock_point;
		}
	}
}

int findSlopes( signed long off_start, signed long off_end, signed long step, unsigned long deriv_limit ) {
	volatile int i = 0;
	signed long buffer[5], deriv, deriv_sign = 0, deriv_max = 0;
	unsigned char pos = 0, data_pos = 0;

	signed long off = off_start;

	for( i = 0; i < 5; ++i )
		buffer[i] = 0;

	while( off < off_end ) {
		off += step;
		*dac[0] = ( (0x7FFF0000u + off) >> 4 ) & 0xFFF0000u;
		for( i=0; i<500*MICROSECOND; ++i );		// Wait a little for changes to propagate
			
		while(!ADCSTA);
		pos = (pos + 1) % 5;
		buffer[ pos ] = (signed long)(ADCDAT >> 16);
			
		// Calculate derivative of recent data
		deriv = 0;
		pos = (pos+1) % 5;
		for(i=0; i<4; ++i) {
			deriv += buffer[ (pos+1) % 5 ] - buffer[ pos ];
			pos = (pos+1) % 5;
		}

		deriv += (buffer[ pos ] - buffer[ (pos+1) % 5 ]) / 4;
		deriv += (buffer[ (pos+4) % 5 ] - buffer[ (pos+2) % 5 ]) / 2;
		deriv /= 6;

		//write(0, (unsigned char*)(&deriv), sizeof(long));

		if( deriv < -deriv_limit || deriv > deriv_limit || deriv*deriv_sign < 0 ) {
			if( deriv_sign != 0 && deriv*deriv_sign > 0 ) {
				DERIVS[ data_pos ].width = off - DERIVS[ data_pos ].center;
				DERIVS[ data_pos ].range = buffer[ (pos-2) % 5 ] - DERIVS[ data_pos ].value;
				if( DERIVS[ data_pos ].range )	DERIVS[ data_pos ].range = -DERIVS[ data_pos ].range;

				DERIVS[ data_pos ].center += DERIVS[ data_pos ].width / 2;
				DERIVS[ data_pos ].value += DERIVS[ data_pos ].range / 2;

				if( data_pos == NDERIVS-1 )
					return NDERIVS;
				data_pos = (data_pos + 1) % NDERIVS;
			}
			deriv_sign = 0;
		} else if( deriv_sign == 0 ) {
			deriv_sign = (deriv < 0? -deriv: deriv) / deriv;
			DERIVS[ data_pos ].max_deriv = deriv_max = deriv*deriv_sign;
			DERIVS[ data_pos ].sign = deriv_sign;

			DERIVS[ data_pos ].center = off;
			DERIVS[ data_pos ].value = buffer[ (pos-2) % 5 ];

		} else if( deriv*deriv_sign > deriv_max ) {
			DERIVS[ data_pos ].max_deriv = deriv*deriv_sign;
		}			
	}

	return data_pos;
}

int findSignal(void) {
	int i = 0;
	const unsigned long offset_max = 50;

	unsigned long best_peak = 0, best_peak_val = 0;
	int nslopes = findSlopes( 0, offset_max*OUTPUT_STEP, OUTPUT_STEP, 300 );
	if( nslopes == 0 )
		return 0;

	for( i = 0; i < nslopes; ++i ) {
		if( DERIVS[i].max_deriv * DERIVS[i].range > best_peak_val ) {
			best_peak = i;
			best_peak_val = DERIVS[i].max_deriv * DERIVS[i].range;
		}
	}

	CHANNELS[0].lock_point = DERIVS[ best_peak ].value;
	CHANNELS[0].output = DERIVS[ best_peak ].center + 0x7FFF0000u;
	return 1;		
}

int scanSignal(void) {
	return 1;
}

int recoverSignal(void) {
	return 1;
}

void IRQ_Handler(void) { 
	readcontrols = 1;
	T2CLRI = 1;
	T2CLRI = 1;
	
	//T3CLRI = 1;
	//T3CLRI = 1;
}
