//`timescale 1ns/100ps
// --------------------------------------------------------------------
// Copyright (c) 2005 by Terasic Technologies Inc. 
// --------------------------------------------------------------------
//
// Permission:
//
//   Terasic grants permission to use and modify this code for use
//   in synthesis for all Terasic Development Boards and Altera Development 
//   Kits made by Terasic.  Other use of this code, including the selling 
//   ,duplication, or modification of any portion is strictly prohibited.
//
// Disclaimer:
//
//   This VHDL/Verilog or C/C++ source code is intended as a design reference
//   which illustrates how these types of functions can be implemented.
//   It is the user's responsibility to verify their design for
//   consistency and functionality through the use of formal
//   verification methods.  Terasic provides no warranty regarding the use 
//   or functionality of this code.
//
// --------------------------------------------------------------------
//           
//                     Terasic Technologies Inc
//                     356 Fu-Shin E. Rd Sec. 1. JhuBei City,
//                     HsinChu County, Taiwan
//                     302
//
//                     web: http://www.terasic.com/
//                     email: support@terasic.com
//
// --------------------------------------------------------------------
//
// Major Functions:	DE2 TOP LEVEL
//
// --------------------------------------------------------------------
//
// Revision History :
// --------------------------------------------------------------------
//   Ver  :| Author            :| Mod. Date :| Changes Made:
//   V1.0 :| Johnny Chen       :| 05/08/19  :|      Initial Revision
//   V1.1 :| Johnny Chen       :| 05/11/16  :|      Add to FLASH Address FL_ADDR[21:20]
//   V1.2 :| Johnny Chen       :| 05/11/16  :|		Fixed ISP1362 INT/DREQ Pin Direction.   
// --------------------------------------------------------------------

module DE2_TOP
	(
		////////////////////	Clock Input	 	////////////////////	 
		input CLOCK_27,							//	27 MHz
		input CLOCK_50,							//	50 MHz
		input EXT_CLOCK,							//	External Clock
		////////////////////	Push Button		////////////////////
		input [3:0] KEY,							//	Pushbutton[3:0]
		////////////////////	DPDT Switch		////////////////////
		input [17:0] SW,							//	Toggle Switch[17:0]
		////////////////////	7-SEG Dispaly	////////////////////
		output [6:0] HEX0,						//	Seven Segment Digit 0
		output [6:0] HEX1,						//	Seven Segment Digit 1
		output [6:0] HEX2,						//	Seven Segment Digit 2
		output [6:0] HEX3,						//	Seven Segment Digit 3
		output [6:0] HEX4,						//	Seven Segment Digit 4
		output [6:0] HEX5,						//	Seven Segment Digit 5
		output [6:0] HEX6,						//	Seven Segment Digit 6
		output [6:0] HEX7,						//	Seven Segment Digit 7
		////////////////////////	LED	////////////////////////
		output [8:0] LEDG,						//	LED Green[8:0]
		output [17:0] LEDR,						//	LED Red[17:0]
		////////////////////////	UART	////////////////////////
		output UART_TXD,							//	UART Transmitter
		input UART_RXD,							//	UART Receiver
		////////////////////////	IRDA	////////////////////////
		output IRDA_TXD,							//	IRDA Transmitter
		input IRDA_RXD,							//	IRDA Receiver
		/////////////////////	SDRAM Interface		////////////////
		inout [15:0] DRAM_DQ,					//	SDRAM Data bus 16 Bits
		output [11:0] DRAM_ADDR,				//	SDRAM Address bus 12 Bits
		output DRAM_LDQM,							//	SDRAM Low-byte Data Mask 
		output DRAM_UDQM,							//	SDRAM High-byte Data Mask
		output DRAM_WE_N,							//	SDRAM Write Enable
		output DRAM_CAS_N,						//	SDRAM Column Address Strobe
		output DRAM_RAS_N,						//	SDRAM Row Address Strobe
		output DRAM_CS_N,							//	SDRAM Chip Select
		output DRAM_BA_0,							//	SDRAM Bank Address 0
		output DRAM_BA_1,							//	SDRAM Bank Address 0
		output DRAM_CLK,							//	SDRAM Clock
		output DRAM_CKE,							//	SDRAM Clock Enable
		////////////////////	Flash Interface		////////////////
		inout [7:0] FL_DQ,						//	FLASH Data bus 8 Bits
		output [21:0] FL_ADDR,					//	FLASH Address bus 22 Bits
		output FL_WE_N,							//	FLASH Write Enable
		output FL_RST_N,							//	FLASH Reset
		output FL_OE_N,							//	FLASH Output Enable
		output FL_CE_N,							//	FLASH Chip Enable
		////////////////////	SRAM Interface		////////////////
		inout [15:0] SRAM_DQ,					//	SRAM Data bus 16 Bits
		output [17:0] SRAM_ADDR,				//	SRAM Address bus 18 Bits
		output SRAM_UB_N,							//	SRAM High-byte Data Mask 
		output SRAM_LB_N,							//	SRAM Low-byte Data Mask 
		output SRAM_WE_N,							//	SRAM Write Enable
		output SRAM_CE_N,							//	SRAM Chip Enable
		output SRAM_OE_N,							//	SRAM Output Enable
		////////////////////	ISP1362 Interface	////////////////
		inout [15:0] OTG_DATA,						//	ISP1362 Data bus 16 Bits
		output [1:0] OTG_ADDR,						//	ISP1362 Address 2 Bits
		output OTG_CS_N,						//	ISP1362 Chip Select
		output OTG_RD_N,						//	ISP1362 Write
		output OTG_WR_N,						//	ISP1362 Read
		output OTG_RST_N,						//	ISP1362 Reset
		output OTG_FSPEED,						//	USB Full Speed,	0 = Enable, Z = Disable
		output OTG_LSPEED,						//	USB Low Speed, 	0 = Enable, Z = Disable
		input OTG_INT0,						//	ISP1362 Interrupt 0
		input OTG_INT1,						//	ISP1362 Interrupt 1
		input OTG_DREQ0,						//	ISP1362 DMA Request 0
		input OTG_DREQ1,						//	ISP1362 DMA Request 1
		output OTG_DACK0_N,					//	ISP1362 DMA Acknowledge 0
		output OTG_DACK1_N,					//	ISP1362 DMA Acknowledge 1
		////////////////////	LCD Module 16X2		////////////////
		inout [7:0] LCD_DATA,						//	LCD Data bus 8 bits
		output LCD_ON,							//	LCD Power ON/OFF
		output LCD_BLON,						//	LCD Back Light ON/OFF
		output LCD_RW,							//	LCD Read/Write Select, 0 = Write, 1 = Read
		output LCD_EN,							//	LCD Enable
		output LCD_RS,							//	LCD Command/Data Select, 0 = Command, 1 = Data
		////////////////////	SD_Card Interface	////////////////
		inout SD_DAT,							//	SD Card Data
		inout SD_DAT3,						//	SD Card Data 3
		inout SD_CMD,							//	SD Card Command Signal
		output SD_CLK,							//	SD Card Clock
		////////////////////	I2C		////////////////////////////
		inout I2C_SDAT,						//	I2C Data
		output I2C_SCLK,						//	I2C Clock
		////////////////////	PS2		////////////////////////////
		input PS2_DAT,						//	PS2 Data
		input PS2_CLK,						//	PS2 Clock
		////////////////////	USB JTAG link	////////////////////
		input TDI,  							// CPLD -> FPGA (data in)
		input TCK,  							// CPLD -> FPGA (clk)
		input TCS,  							// CPLD -> FPGA (CS)
	   output TDO,  							// FPGA -> CPLD (data out)
		////////////////////	VGA		////////////////////////////
		output VGA_CLK,   						//	VGA Clock
		output VGA_HS,							//	VGA H_SYNC
		output VGA_VS,							//	VGA V_SYNC
		output VGA_BLANK,						//	VGA BLANK
		output VGA_SYNC,						//	VGA SYNC
		output [9:0] VGA_R,   						//	VGA Red[9:0]
		output [9:0] VGA_G,	 						//	VGA Green[9:0]
		output [9:0] VGA_B,  						//	VGA Blue[9:0]
		////////////	Ethernet Interface	////////////////////////
		inout [15:0] ENET_DATA,				//	DM9000A DATA bus 16Bits
		output ENET_CMD,						//	DM9000A Command/Data Select, 0 = Command, 1 = Data
		output ENET_CS_N,						//	DM9000A Chip Select
		output ENET_WR_N,						//	DM9000A Write
		output ENET_RD_N,						//	DM9000A Read
		output ENET_RST_N,					//	DM9000A Reset
		input ENET_INT,						//	DM9000A Interrupt
		output ENET_CLK,						//	DM9000A Clock 25 MHz
		////////////////	Audio CODEC		////////////////////////
		inout AUD_ADCLRCK,					//	Audio CODEC ADC LR Clock
		input AUD_ADCDAT,						//	Audio CODEC ADC Data
		inout AUD_DACLRCK,					//	Audio CODEC DAC LR Clock
		output AUD_DACDAT,					//	Audio CODEC DAC Data
		inout AUD_BCLK,						//	Audio CODEC Bit-Stream Clock
		output AUD_XCK,						//	Audio CODEC Chip Clock
		////////////////	TV Decoder		////////////////////////
		input [7:0] TD_DATA,    			//	TV Decoder Data bus 8 bits
		input TD_HS,							//	TV Decoder H_SYNC
		input TD_VS,							//	TV Decoder V_SYNC
		output TD_RESET,						//	TV Decoder Reset
		////////////////////	GPIO	////////////////////////////
		inout [35:0] GPIO_0,					//	GPIO Connection 0
		output [35:0] GPIO_1					//	GPIO Connection 1
	);

//	Turn off all displays
//assign	HEX0		=	7'h7f;
//assign	HEX1		=	7'h7f;
//assign	HEX2		=	7'h7f;
//assign	HEX3		=	7'h7f;
//assign	HEX4		=	7'h7f;
//assign	HEX5		=	7'h7f;
//assign	HEX6		=	7'h7f;
//assign	HEX7		=	7'h7f;
assign	LEDG	   =	9'h000;
assign	LEDR		=	18'h00000;
assign	LCD_ON	=	1'b0;
assign	LCD_BLON	=	1'b0;

// Ground data and control pins
assign	VGA_R			=	10'h000;
assign	VGA_G			=	10'h000;
assign	VGA_B			=	10'h000;

assign 	UART_TXD		=	1'b0;
assign	IRDA_TXD		=	1'b0;

assign	DRAM_LDQM	=	1'b0;
assign	DRAM_UDQM	=	1'b0;
assign	DRAM_WE_N	= 	1'b1;
assign	DRAM_CAS_N	=	1'b1;
assign	DRAM_RAS_N	=	1'b1;
assign	DRAM_CS_N	=	1'b1;
assign	DRAM_BA_0	=	1'b1;
assign	DRAM_BA_1	=	1'b1;
assign	DRAM_CLK		=	1'b0;
assign	DRAM_CKE		=	1'b0;

assign	FL_WE_N		=	1'b1;
assign	FL_RST_N		=	1'b1;
assign	FL_OE_N		=	1'b1;
assign	FL_CE_N		=	1'b1;

//assign	SRAM_UB_N	=	1'b1;
//assign	SRAM_LB_N	=	1'b1;
//assign	SRAM_WE_N	=	1'b1;
//assign	SRAM_CE_N	=	1'b1;
//assign	SRAM_OE_N	=	1'b1;

assign	OTG_CS_N		= 	1'b1;
assign	OTG_RD_N		=	1'b1;
assign	OTG_WR_N		=	1'b1;
assign	OTG_RST_N	=	1'b1;
assign	OTG_FSPEED	=	1'b0;
assign	OTG_LSPEED	=	1'b0;
assign	OTG_DACK0_N	=	1'b1;
assign	OTG_DACK1_N	=	1'b1;

assign	LCD_RW		=	1'b0;
assign	LCD_EN		=	1'b0;
assign	LCD_RS		=	1'b0;

assign 	SD_CLK		=	1'b0;
assign	I2C_SCLK		=	1'b0;
assign	TDO			=	1'b0;

assign	VGA_CLK		=	1'b0;
assign	VGA_HS		=	1'b0;
assign	VGA_VS		=	1'b0;
assign	VGA_BLANK	=	1'b0;
assign	VGA_SYNC		=	1'b0;

//assign	ENET_CMD		=	1'b0;
//assign	ENET_CS_N	=	1'b1;
//assign	ENET_WR_N	=	1'b1;
//assign	ENET_RD_N	=	1'b1;
//assign	ENET_RST_N	=	1'b1;
//assign	ENET_CLK		=	1'b0;

assign	AUD_DACDAT	=	1'b0;
assign	AUD_XCK		=	1'b0;

assign	TD_RESET 		= 1'b1;

// Ground address pins
assign	DRAM_ADDR 	=	12'h000;
assign	FL_ADDR		= 	22'h000000;
//assign	SRAM_ADDR	=	18'h00000;
assign	OTG_ADDR		=	2'h0;

//	All inout port turn to tri-state
assign	DRAM_DQ		=	16'hzzzz;
assign	FL_DQ			=	8'hzz;
//assign	SRAM_DQ		=	16'hzzzz;
assign	OTG_DATA		=	16'hzzzz;
assign	LCD_DATA		=	8'hzz;
assign	SD_DAT		=	1'bz;
assign	SD_DAT3		=	1'bz;
assign	SD_CMD		=	1'bz;
assign	I2C_SDAT		=	1'bz;
//assign	ENET_DATA	=	16'hzzzz;
assign	AUD_ADCLRCK	=	1'bz;
assign	AUD_DACLRCK	=	1'bz;
assign	AUD_BCLK		=	1'bz;
assign	GPIO_0		=	36'hzzzzzzzzz;
assign	GPIO_1[35:5]		=	31'h00000000;



///////////////////////////////////
////  Ethernet Phy/Mac Logic   ////
///////////////////////////////////

//	DM9000A Clock 25 MHz
reg CLOCK_25;
always@(posedge CLOCK_50) begin
  CLOCK_25 <= ~CLOCK_25;
end

reg CLOCK_3, CLOCK_6, CLOCK_12;
reg [2:0] CLOCK_SLOW;

always@(posedge CLOCK_25) begin
	CLOCK_12 <= ~CLOCK_12;
end
always@(posedge CLOCK_12) begin
	CLOCK_6 <= ~CLOCK_6;
end
always@(posedge CLOCK_6) begin
	CLOCK_3 <= ~CLOCK_3;
end
always@(posedge CLOCK_3) begin
	CLOCK_SLOW <= CLOCK_SLOW + 3'd1;
end

reg KEY3_L, KEY2_L, KEY1_L;
always@(posedge CLOCK_25) begin
  KEY3_L <= KEY[3];
  KEY1_L <= KEY[1];
end

always@(posedge CLOCK_12) begin
  KEY2_L <= KEY[2];
end

wire KEY3Pulse = ~KEY[3] & KEY3_L;
wire KEY2Pulse = ~KEY[2] & KEY2_L;
wire KEY1Pulse = ~KEY[1] & KEY1_L;

reg [3:0] hex0, hex1, hex2, hex3, hex4, hex5, hex6, hex7;
HexDigit digit0( HEX0, hex0 );
HexDigit digit1( HEX1, hex1 );
HexDigit digit2( HEX2, hex2 );
HexDigit digit3( HEX3, hex3 );
HexDigit digit4( HEX4, hex4 );
HexDigit digit5( HEX5, hex5 );
HexDigit digit6( HEX6, hex6 );
HexDigit digit7( HEX7, hex7 );

wire sram_cyc, sram_stb, sram_we, sram_ack;
wire [15:0] sram_dat_i, sram_dat_o;
wire [17:0] sram_adr;

wire net_dac_trigger;
wire net_sram_cyc, net_sram_stb, net_sram_we, net_sram_ack;
wire [15:0] net_sram_dat_i, net_sram_dat_o;
wire [17:0] net_sram_adr;

wire dac_sram_cyc, dac_sram_stb, dac_sram_we, dac_sram_ack;
wire [15:0] dac_sram_dat_i, dac_sram_dat_o;
wire [17:0] dac_sram_adr;

always @(posedge CLOCK_25) begin
	if( ~SW[17] & sram_ack ) begin
		//hex7 <= src_ip_o[31:28];
		//hex6 <= src_ip_o[27:24];
		//hex5 <= src_ip_o[23:20];
		//hex4 <= src_ip_o[19:16];
		
		hex3 <= sram_dat_o[15:12];
		hex2 <= sram_dat_o[11:8];
		hex1 <= sram_dat_o[7:4];
		hex0 <= sram_dat_o[3:0];
	end
	
	hex4 <= GPIO_1[4:2];
end

assign sram_cyc = 	net_sram_cyc? net_sram_cyc: dac_sram_cyc; 
assign sram_stb = 	net_sram_cyc? net_sram_stb: dac_sram_stb; 
assign sram_we = 		net_sram_cyc? net_sram_we: dac_sram_we;
 
assign sram_adr = 	net_sram_cyc? net_sram_adr: dac_sram_adr;
assign sram_dat_i = 	net_sram_cyc? net_sram_dat_o: 16'b0;
assign dac_sram_dat_i = ~net_sram_cyc? sram_dat_o: 16'b0; 

assign net_sram_ack = net_sram_cyc? sram_ack: 1'b0;
assign dac_sram_ack = ~net_sram_cyc? sram_ack: 1'b0;

/*
assign sram_cyc = SW[17]? net_sram_cyc: ~KEY[2]; 
assign sram_stb = SW[17]? net_sram_stb: ~KEY[2]; 
assign sram_we = SW[17]? net_sram_we: 1'b0;
 
assign sram_adr = SW[17]? net_sram_adr: {12'h000, SW[5:0]};
assign sram_dat_i = SW[17]? net_sram_dat_o: 16'h0000; 

assign net_sram_ack = SW[17]? sram_ack: 1'b0;
*/

SRAM TheSRAM(
	.wb_clk_i( CLOCK_25 ),
	
	.wb_cyc_i( sram_cyc ),
	.wb_stb_i( sram_stb ),
	.wb_we_i( sram_we ),
	.wb_ack_o( sram_ack ),

	.wb_adr_i( sram_adr ),
	.wb_dat_i( sram_dat_i ),
	.wb_dat_o( sram_dat_o ),

	// SRAM Interface
	.sram_ce_n( SRAM_CE_N ),	// SRAM Chip Enable
	.sram_oe_n( SRAM_OE_N ),	// SRAM Output Enable
	.sram_we_n( SRAM_WE_N ),	// SRAM Write Enable
	.sram_lb_n( SRAM_LB_N ),	// SRAM Lower-byte Control
	.sram_ub_n( SRAM_UB_N ),	// SRAM Upper-byte Control

	.sram_data( SRAM_DQ ),
	.sram_addr( SRAM_ADDR )
	);

wire dac_stb;
assign dac_stb = net_dac_trigger; // || KEY2Pulse;

DAC #( .UPDATE_TIME( 512 ) ) TheDAC(

	.wb_clk_i( CLOCK_12 ),
	.wb_rst_i( ~KEY[0] ),
	
	.wb_cyc_i( 1'b1 ),
	.wb_stb_i( dac_stb ),
	.wb_we_i( 1'b1 ),
	
	.sram_wb_cyc_o( dac_sram_cyc ),
	.sram_wb_stb_o( dac_sram_stb ),
	.sram_wb_we_o( dac_sram_we ),
	.sram_wb_ack_i( dac_sram_ack ),
	
	.sram_wb_adr_o( dac_sram_adr ),
	.sram_wb_dat_i( dac_sram_dat_i ),
	
	.serial_clk_o( GPIO_1[0] ),
	.serial_cyc_o( GPIO_1[1] ),
	.serial_dat_o( {GPIO_1[4:2]} )
	//.serial_dat_i
	);
	
Network TheNet(
	.wb_clk_i( CLOCK_25 ),
	.wb_rst_i( ~KEY[0] ),
	.wb_init_i( KEY1Pulse ),
	
	.trigger_dac( net_dac_trigger ),
	
	// Wishbone master interface to SRAM
	.sram_wb_cyc_o( net_sram_cyc ),
	.sram_wb_stb_o( net_sram_stb ),
	.sram_wb_we_o( net_sram_we ),
	.sram_wb_ack_i( net_sram_ack ),	
	
	.sram_wb_adr_o( net_sram_adr ),
	.sram_wb_dat_o( net_sram_dat_o ),
	
	// Non-Wishbone ethernet DM9000A interface
	.ENET_DATA( ENET_DATA ),
	.ENET_CMD( ENET_CMD ),
	.ENET_CS_N( ENET_CS_N ),
	.ENET_WR_N( ENET_WR_N ),
	.ENET_RD_N( ENET_RD_N ),
	.ENET_RST_N( ENET_RST_N ),
	.ENET_INT( ENET_INT ),
	.ENET_CLK( ENET_CLK )
	);
	
endmodule

// Decode one hex digit for LED 7-seg display
module HexDigit(
	output reg [6:0] segs,
	input [3:0] num
);
	always @(*)
	begin
		case (num)
				4'h0: segs = 7'b1000000;
				4'h1: segs = 7'b1111001;
				4'h2: segs = 7'b0100100;
				4'h3: segs = 7'b0110000;
				4'h4: segs = 7'b0011001;
				4'h5: segs = 7'b0010010;
				4'h6: segs = 7'b0000010;
				4'h7: segs = 7'b1111000;
				4'h8: segs = 7'b0000000;
				4'h9: segs = 7'b0010000;
				4'ha: segs = 7'b0001000;
				4'hb: segs = 7'b0000011;
				4'hc: segs = 7'b1000110;
				4'hd: segs = 7'b0100001;
				4'he: segs = 7'b0000110;
				4'hf: segs = 7'b0001110;
				default segs = 7'b1111111;
		endcase
	end
endmodule
