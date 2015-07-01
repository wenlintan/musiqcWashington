module test();
	integer i;

		////////////////////	Clock Input	 	////////////////////	 
		wire CLOCK_27;						//	27 MHz
		reg CLOCK_50;						//	50 MHz
		wire EXT_CLOCK;						//	External Clock
		////////////////////	Push Button		////////////////////
		reg [3:0] KEY;						//	Pushbutton[3:0]
		////////////////////	DPDT Switch		////////////////////
		wire [17:0] SW;						//	Toggle Switch[17:0]
		////////////////////	7-SEG Dispaly	////////////////////
		wire [6:0] HEX0;						//	Seven Segment Digit 0
		wire [6:0] HEX1;						//	Seven Segment Digit 1
		wire [6:0] HEX2;						//	Seven Segment Digit 2
		wire [6:0] HEX3;						//	Seven Segment Digit 3
		wire [6:0] HEX4;						//	Seven Segment Digit 4
		wire [6:0] HEX5;						//	Seven Segment Digit 5
		wire [6:0] HEX6;						//	Seven Segment Digit 6
		wire [6:0] HEX7;						//	Seven Segment Digit 7
		////////////////////////	LED	////////////////////////
		wire [8:0] LEDG;					//	LED Green[8:0]
		wire [17:0] LEDR;					//	LED Red[17:0]
		////////////////////////	UART	////////////////////////
		wire UART_TXD;						//	UART Transmitter
		wire UART_RXD;						//	UART Receiver
		////////////////////////	IRDA	////////////////////////
		wire IRDA_TXD;						//	IRDA Transmitter
		wire IRDA_RXD;						//	IRDA Receiver
		/////////////////////	SDRAM Interface		////////////////
		wire [15:0] DRAM_DQ;						//	SDRAM Data bus 16 Bits
		wire [11:0] DRAM_ADDR;						//	SDRAM Address bus 12 Bits
		wire DRAM_LDQM;						//	SDRAM Low-byte Data Mask 
		wire DRAM_UDQM;						//	SDRAM High-byte Data Mask
		wire DRAM_WE_N;						//	SDRAM Write Enable
		wire DRAM_CAS_N;						//	SDRAM Column Address Strobe
		wire DRAM_RAS_N;						//	SDRAM Row Address Strobe
		wire DRAM_CS_N;						//	SDRAM Chip Select
		wire DRAM_BA_0;						//	SDRAM Bank Address 0
		wire DRAM_BA_1;						//	SDRAM Bank Address 0
		wire DRAM_CLK;						//	SDRAM Clock
		wire DRAM_CKE;						//	SDRAM Clock Enable
		////////////////////	Flash Interface		////////////////
		wire [7:0] FL_DQ;							//	FLASH Data bus 8 Bits
		wire [21:0] FL_ADDR;						//	FLASH Address bus 22 Bits
		wire FL_WE_N;						//	FLASH Write Enable
		wire FL_RST_N;						//	FLASH Reset
		wire FL_OE_N;						//	FLASH Output Enable
		wire FL_CE_N;						//	FLASH Chip Enable
		////////////////////	SRAM Interface		////////////////
		wire [15:0] SRAM_DQ;						//	SRAM Data bus 16 Bits
		wire [17:0] SRAM_ADDR;						//	SRAM Address bus 18 Bits
		wire SRAM_UB_N;						//	SRAM High-byte Data Mask 
		wire SRAM_LB_N;						//	SRAM Low-byte Data Mask 
		wire SRAM_WE_N;						//	SRAM Write Enable
		wire SRAM_CE_N;						//	SRAM Chip Enable
		wire SRAM_OE_N;						//	SRAM Output Enable
		////////////////////	ISP1362 Interface	////////////////
		wire [15:0] OTG_DATA;						//	ISP1362 Data bus 16 Bits
		wire [1:0] OTG_ADDR;						//	ISP1362 Address 2 Bits
		wire OTG_CS_N;					//	ISP1362 Chip Select
		wire OTG_RD_N;						//	ISP1362 Write
		wire OTG_WR_N;						//	ISP1362 Read
		wire OTG_RST_N;						//	ISP1362 Reset
		wire OTG_FSPEED;						//	USB Full Speed;	0 = Enable; Z = Disable
		wire OTG_LSPEED;						//	USB Low Speed; 	0 = Enable; Z = Disable
		wire OTG_INT0;						//	ISP1362 Interrupt 0
		wire OTG_INT1;						//	ISP1362 Interrupt 1
		wire OTG_DREQ0;						//	ISP1362 DMA Request 0
		wire OTG_DREQ1;						//	ISP1362 DMA Request 1
		wire OTG_DACK0_N;					//	ISP1362 DMA Acknowledge 0
		wire OTG_DACK1_N;					//	ISP1362 DMA Acknowledge 1
		////////////////////	LCD Module 16X2		////////////////
		wire [7:0] LCD_DATA;						//	LCD Data bus 8 bits
		wire LCD_ON;							//	LCD Power ON/OFF
		wire LCD_BLON;						//	LCD Back Light ON/OFF
		wire LCD_RW;							//	LCD Read/Write Select; 0 = Write; 1 = Read
		wire LCD_EN;							//	LCD Enable
		wire LCD_RS;							//	LCD Command/Data Select; 0 = Command; 1 = Data
		////////////////////	SD_Card Interface	////////////////
		wire SD_DAT;							//	SD Card Data
		wire SD_DAT3;						//	SD Card Data 3
		wire SD_CMD;							//	SD Card Command Signal
		wire SD_CLK;							//	SD Card Clock
		////////////////////	I2C		////////////////////////////
		wire I2C_SDAT;						//	I2C Data
		wire I2C_SCLK;						//	I2C Clock
		////////////////////	PS2		////////////////////////////
		wire PS2_DAT;						//	PS2 Data
		wire PS2_CLK;						//	PS2 Clock
		////////////////////	USB JTAG link	////////////////////
		wire TDI;  							// CPLD -> FPGA (data in)
		wire TCK;  							// CPLD -> FPGA (clk)
		wire TCS;  							// CPLD -> FPGA (CS)
		wire TDO;  							// FPGA -> CPLD (data out)
		////////////////////	VGA		////////////////////////////
		wire VGA_CLK;   						//	VGA Clock
		wire VGA_HS;							//	VGA H_SYNC
		wire VGA_VS;							//	VGA V_SYNC
		wire VGA_BLANK;						//	VGA BLANK
		wire VGA_SYNC;						//	VGA SYNC
		wire [9:0] VGA_R;   						//	VGA Red[9:0]
		wire [9:0] VGA_G;	 						//	VGA Green[9:0]
		wire [9:0] VGA_B;  						//	VGA Blue[9:0]
		////////////	Ethernet Interface	////////////////////////
		wire [15:0] ENET_DATA;				//	DM9000A DATA bus 16Bits
		wire ENET_CMD;						//	DM9000A Command/Data Select; 0 = Command; 1 = Data
		wire ENET_CS_N;						//	DM9000A Chip Select
		wire ENET_WR_N;						//	DM9000A Write
		wire ENET_RD_N;						//	DM9000A Read
		wire ENET_RST_N;					//	DM9000A Reset
		wire ENET_INT;						//	DM9000A Interrupt
		wire ENET_CLK;						//	DM9000A Clock 25 MHz
		////////////////	Audio CODEC		////////////////////////
		wire AUD_ADCLRCK;					//	Audio CODEC ADC LR Clock
		wire AUD_ADCDAT;						//	Audio CODEC ADC Data
		wire AUD_DACLRCK;					//	Audio CODEC DAC LR Clock
		wire AUD_DACDAT;					//	Audio CODEC DAC Data
		wire AUD_BCLK;						//	Audio CODEC Bit-Stream Clock
		wire AUD_XCK;						//	Audio CODEC Chip Clock
		////////////////	TV Decoder		////////////////////////
		wire [7:0] TD_DATA;    			//	TV Decoder Data bus 8 bits
		wire TD_HS;							//	TV Decoder H_SYNC
		wire TD_VS;							//	TV Decoder V_SYNC
		wire TD_RESET;						//	TV Decoder Reset
		////////////////////	GPIO	////////////////////////////
		wire [35:0] GPIO_0;					//	GPIO Connection 0
		wire [35:0] GPIO_1;					//	GPIO Connection 1

	DE2_TOP de2top(
		.CLOCK_27(CLOCK_27),
		.CLOCK_50(CLOCK_50),
		.EXT_CLOCK(EXT_CLOCK),
		.KEY(KEY),
		.SW(SW),
		.HEX0(HEX0),
		.HEX1(HEX1),
		.HEX2(HEX2),
		.HEX3(HEX3),
		.HEX4(HEX4),
		.HEX5(HEX5),
		.HEX6(HEX6),
		.HEX7(HEX7),
		.LEDG(LEDG),
		.LEDR(LEDR),
		.UART_TXD(UART_TXD),
		.UART_RXD(UART_RXD),
		.IRDA_TXD(IRDA_TXD),
		.IRDA_RXD(IRDA_RXD),
		.DRAM_DQ(DRAM_DQ),
		.DRAM_ADDR(DRAM_ADDR),
		.DRAM_LDQM(DRAM_LDQM),
		.DRAM_UDQM(DRAM_UDQM),
		.DRAM_WE_N(DRAM_WE_N),
		.DRAM_CAS_N(DRAM_CAS_N),
		.DRAM_RAS_N(DRAM_RAS_N),
		.DRAM_CS_N(DRAM_CS_N),
		.DRAM_BA_0(DRAM_BA_0),
		.DRAM_BA_1(DRAM_BA_1),
		.DRAM_CLK(DRAM_CLK),
		.DRAM_CKE(DRAM_CKE),
		.FL_DQ(FL_DQ),
		.FL_ADDR(FL_ADDR),
		.FL_WE_N(FL_WE_N),
		.FL_RST_N(FL_RST_N),
		.FL_OE_N(FL_OE_N),
		.FL_CE_N(FL_CE_N),
		.SRAM_DQ(SRAM_DQ),
		.SRAM_ADDR(SRAM_ADDR),
		.SRAM_UB_N(SRAM_UB_N),
		.SRAM_LB_N(SRAM_LB_N),
		.SRAM_WE_N(SRAM_WE_N),
		.SRAM_CE_N(SRAM_CE_N),
		.SRAM_OE_N(SRAM_OE_N),
		.OTG_DATA(OTG_DATA),
		.OTG_ADDR(OTG_ADDR),
		.OTG_CS_N(OTG_CS_N),
		.OTG_RD_N(OTG_RD_N),
		.OTG_WR_N(OTG_WR_N),
		.OTG_RST_N(OTG_RST_N),
		.OTG_FSPEED(OTG_FSPEED),
		.OTG_LSPEED(OTG_LSPEED),
		.OTG_INT0(OTG_INT0),
		.OTG_INT1(OTG_INT1),
		.OTG_DREQ0(OTG_DREQ0),
		.OTG_DREQ1(OTG_DREQ1),
		.OTG_DACK0_N(OTG_DACK0_N),
		.OTG_DACK1_N(OTG_DACK1_N),
		.LCD_DATA(LCD_DATA),
		.LCD_ON(LCD_ON),
		.LCD_BLON(LCD_BLON),
		.LCD_RW(LCD_RW),
		.LCD_EN(LCD_EN),
		.LCD_RS(LCD_RS),
		.SD_DAT(SD_DAT),
		.SD_DAT3(SD_DAT3),
		.SD_CMD(SD_CMD),
		.SD_CLK(SD_CLK),
		.I2C_SDAT(I2C_SDAT),
		.I2C_SCLK(I2C_SCLK),
		.PS2_DAT(PS2_DAT),
		.PS2_CLK(PS2_CLK),
		.TDI(TDI),
		.TCK(TCK),
		.TCS(TCS),
		.TDO(TDO),
		.VGA_CLK(VGA_CLK),
		.VGA_HS(VGA_HS),
		.VGA_VS(VGA_VS),
		.VGA_BLANK(VGA_BLANK),
		.VGA_SYNC(VGA_SYNC),
		.VGA_R(VGA_R),
		.VGA_G(VGA_G),
		.VGA_B(VGA_B),
		.ENET_DATA(ENET_DATA),
		.ENET_CMD(ENET_CMD),
		.ENET_CS_N(ENET_CS_N),
		.ENET_WR_N(ENET_WR_N),
		.ENET_RD_N(ENET_RD_N),
		.ENET_RST_N(ENET_RST_N),
		.ENET_INT(ENET_INT),
		.ENET_CLK(ENET_CLK),
		.AUD_ADCLRCK(AUD_ADCLRCK),
		.AUD_ADCDAT(AUD_ADCDAT),
		.AUD_DACLRCK(AUD_DACLRCK),
		.AUD_DACDAT(AUD_DACDAT),
		.AUD_BCLK(AUD_BCLK),
		.AUD_XCK(AUD_XCK),
		.TD_DATA(TD_DATA),
		.TD_HS(TD_HS),
		.TD_VS(TD_VS),
		.TD_RESET(TD_RESET),
		.GPIO_0(GPIO_0),
		.GPIO_1(GPIO_1) );

	initial begin
		de2top.CLOCK_25 = 1'b0;

		$display ("time\t state cmd, rd, wr, dat");
		$monitor ("%g\t %b %b %b %b %b %h", $time, de2top.EthernetInterface.reg_done, de2top.EthernetInterface.state, ENET_CMD, ENET_RD_N, ENET_WR_N, ENET_DATA );

		KEY = 4'b0;
		KEY[2] = 1;
		KEY[3] = 1;
		#1 CLOCK_50 = 1'b0;
		#1 CLOCK_50 = 1'b1;
		#1 CLOCK_50 = 1'b0;
		#1 CLOCK_50 = 1'b1;

		KEY[0] = 1;
		#1 CLOCK_50 = 1'b0;		
		#1 CLOCK_50 = 1'b1;
		#1 CLOCK_50 = 1'b0;
		#1 CLOCK_50 = 1'b1;

		KEY[2] = 0;
		for( i = 0; i < 50000; i=i+1 ) begin
			#1 CLOCK_50 = 1'b0;
			#1 CLOCK_50 = 1'b1;
		end
		
		KEY[3] = 0;
		for( i = 0; i < 50000; i=i+1 ) begin
			#1 CLOCK_50 = 1'b0;
			#1 CLOCK_50 = 1'b1;
		end

		#10 $finish;
	end

endmodule
