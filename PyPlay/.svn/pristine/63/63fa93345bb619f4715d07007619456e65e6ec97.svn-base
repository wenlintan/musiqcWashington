// PILock algorithm for ADuC7020 microcontroller
// Author: Matt Dietrich
// v1.0 May 1, 2009
// v1.1 May 4, 2009
// Solved Problem with properly reading out gain pots by
// adding a delay.  Fine tuned gains for fiber laser
// v1.2 May 28, 2009
// Introduced PERRORSHIFT to fix problem with rampref, added
// check if ramp width is very small then just make it zero
// v1.3 June 17, 2009
// Added mode that fixes i gain and changes the usual i gain pot
// to d gain.  Uncomment define DERIV_MODE lines to enable.
// v1.4 July 17, 2009
// Added option for filtering.  Performs generic z-domain filtering.
// To enable, define FILTERING and set FILTER_SIZE to the number
// of coefficients in your transfer function.  Sampling freq is ~200 KHz
// with filtering on.

// TODO
// * Threshold.  Should have a button to show threshold level, and another
// to enable threshold at all.
// * Computer control.  Computer interface to set gain parameters.

#include "aduc7020.h"
#include "pwm.h"

// 41 MHz PLL Clock
#define CLOCK 41779200
#define MICROSECOND 42

/* All these are defined as 32-bit longs so that the lower 24 bits   *
 * can be compared with equal footing to the 24 bits used in output. *
 * This has the added benefit of introducing a kind of decimal point *
 * since bits 12-23 can be thought of as "whole numbers" and 0-11 as *
 * fractional.  This is useful for the gains especially, since the   *
 * optimal gain is likely not an integer.  Since error has to be     *
 * negative sometimes, we have to allow for signed values.  This is  *
 * ok though, since the restriction that output be between ramplow   *
 * and ramphigh prevents us from any wierdness wrt the DAC.          */


volatile int readcontrols;
// Debug mode causes green LED to flash at the sampling frequency
//#define DEBUG_MODE 1
#define DERIV_MODE 1

enum{ NCHANNELS = 3 };
volatile unsigned long* dac[3] = { &DAC2DAT, &DAC3DAT, &DAC0DAT };
volatile unsigned long* pwm[3] = { &PWMCH1, &PWMCH2, &PWMCH0 };

typedef struct {
	unsigned long pshift, pgain, ishift, igain, dgain;
	unsigned long lock_point;

	signed long integral, olderror;
	unsigned long output;
} ChannelData;

ChannelData CHANNELS[ NCHANNELS ];
const signed long INTEGRAL_LIMIT = 0x3FFF00;

signed long error;
signed long error_buffer[NCHANNELS];
unsigned long total_error;

// Functions run from flash memory are slow, since it takes two clock
// cycles to read each command.  Put function in .data section for speed.

int getparams(void);
void lockMode(void);// __attribute__((section(".data")));
void IRQ_Handler(void);

int getchar(void);
int putchar(int ch);
int write(int file, unsigned char * ptr, int len);
void read_long(int file, unsigned long * ptr);

int main(void) {
	int i;
	
	// For some reason the default is to divide down the clock
	// by 8 to 5 MHz.  But I have a need... for speed!
	POWKEY1 = 0x01;
	POWCON = 0;
	POWKEY2 = 0xF4;

	// Enable timer wakeup interrupt
	IRQEN = WAKEUP_TIMER_BIT;

	// Setup timer 2 to increment at 32168 Hz, and to count down from 32170 to
	// obtain ~1 Hz.  Creates the only IRQ, which sets a flag to reread P0.5.
	T2LD = 32170;
	T2CON = (1 << 7)|(1 << 10)|(1 << 6);

	REFCON = 1;				// Connect internal VREF  
	ADCCON = 0x0720;		// Turn on ADC, single ended read, 16 clock read time

	// Initialize DACs to use AVDD pin (use 0x12 to use VRef pin instead)
	// DACs 0, 2 and 3 control heaters, DAC1 controls error LED
	DAC0CON = DAC1CON = DAC2CON = DAC3CON = 0x12; //0x13;
	DAC0DAT = DAC1DAT = DAC2DAT = DAC3DAT = 0;
	
	GP1CON = 0x30000011;	// Set P1.0 and P1.1 to uart tx/rx, set P1.7 to PLA0 out
	GP3CON = 0x00010101;	// Set P3.0, 3.2, 3.4 to PWM internally
	GP4CON = 0x00000300;	// Set P4.2 (coincidentally LED) to PLA10 out
	GP0DAT = 0x00000000;	// Set P0.5 to input (activates feedback lock)
	
	// Start setting up UART at 19200 bps
	COMIEN0 = 0;
   	COMCON0 = 0x080;		// Setting DLAB
   	COMDIV0 = 0x044;		// Setting DIV0 and DIV1 to DL calculated
   	COMDIV1 = 0x000;
   	COMCON0 = 0x007;		// Clearing DLAB

	// Turn on PWM and set frequency to lowest possible ~300Hz (at 40MHz)
	PWMCON = 1;
	PWMDAT0 = 0xFFFF; //0xFFFF;
	PWMCH0 = 0x3FFF;
	PWMCH1 = 0x0; //0x5FFF;
	PWMCH2 = 0xCFFF; //0x3FFF;
	
	// Setup PLA blocks to forward PWM signals
	//PLAELM12 = 0x0035;		// set PLA12 to accept input from PWM
	//PLAELM15 = 0x0459;		// route through PLA15
	//PLAELM0  = 0x0059;		// output from PLA0
	
	//PLAELM10 = 0x0035;		// set PLA10 to accept input from PWM and output
	
	for(i=0; i<500*MICROSECOND; i++);		//Wait at least 500 uS for ADC
	write(0, (unsigned char*)"Start\n", 6);

	// Set initial channel data
	for(i=0; i < NCHANNELS; ++i ) {
		CHANNELS[i].pshift = 2;
		CHANNELS[i].pgain = 100;//8;
		CHANNELS[i].ishift = 8;//10;
		CHANNELS[i].igain = 1;
		CHANNELS[i].dgain = 0;
		CHANNELS[i].lock_point = 0x7ff;
	}
	
	for(;;) {
		if( getparams() )	lockMode();
		else				while( !readcontrols );
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
	unsigned long in = 0;
	for(j=0; j<sizeof(long); j++)
		in |= ((unsigned long)getchar() & 0xFF) << j*8;
		
	*ptr = in;
}

/* Get all the various control parameters.  This consumes quite a few clock cycles *
 * human responsivity not very important, so use sparingly.  I use the timer to    *
 * count out time at 10 Hz.                                                        */

int getparams(void) {
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

void lockMode(void) {
	signed long delta;
	volatile int i, j;

	while(!readcontrols) {
#ifdef DEBUG_MODE
		GP4DAT ^= 0x00040000;	// For testing sampling rate
#endif
		while(!(PWMSTA & 0x1));

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

			if( delta > 0xFFFF )			CHANNELS[j].output = 0xFFFF;
			else if( delta < 0 )			CHANNELS[j].output = 0;
			else							CHANNELS[j].output = delta;
			//CHANNELS[j].output = 0;

			// Output the upper 12 bits of output
			// Lower bits represent fractions of a single output level
			//*dac[j] = (CHANNELS[j].output >> 4) & 0xFFF0000;
			if( pwm[j] )	*pwm[j] = (signed long)((CHANNELS[j].output >> 0) & 0xFFFF) - 0x7FFF;
			
			ADCCP = j;
			ADCCON |= 0x83;  // Continuous capture mode
			for(i=0; i<20*MICROSECOND; i++);
			ADCCON &= ~0x80;

			while(!ADCSTA);
			error_buffer[j] = -((signed long)(ADCDAT >> 16) - CHANNELS[j].lock_point);
		}

		//if(total_error > 0xFFF)		total_error = 0xFFF;
		//DAC1DAT = (total_error << 20) >> 4;
		while(PWMSTA & 0x1);
	}
}

void IRQ_Handler(void) { 
	readcontrols = 1;
	T2CLRI = 1;
	T2CLRI = 1;
}
