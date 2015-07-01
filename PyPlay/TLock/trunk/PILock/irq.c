#include "ADuC7020.h"

void	ADI_IRQ_Interrupt_Setup(void) __attribute__ ((interrupt ("IRQ")));
void	ADI_SWI_Interrupt_Setup(void) __attribute__ ((interrupt ("SWI")));
void	ADI_FIQ_Interrupt_Setup(void) __attribute__ ((interrupt ("FIQ")));
void	ADI_UNDEF_Interrupt_Setup(void) __attribute__ ((interrupt ("UNDEF")));
void	ADI_PABORT_Interrupt_Setup(void) __attribute__ ((interrupt ("PABORT")));
void	ADI_DABORT_Interrupt_Setup(void)  __attribute__ ((interrupt ("DABORT")));

void	ADI_IRQ_Interrupt_Setup(void) 
{
	IRQ_Handler();
}

void	ADI_FIQ_Interrupt_Setup(void) 
{

}

void	ADI_SWI_Interrupt_Setup(void) 
{

}

void	ADI_UNDEF_Interrupt_Setup(void) 
{

}

void	ADI_PABORT_Interrupt_Setup(void) 
{

}

void	ADI_DABORT_Interrupt_Setup(void) 
{

}

