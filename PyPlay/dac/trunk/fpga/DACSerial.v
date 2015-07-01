
module DACSerial( 
	input CLOCK_50,
	input [3:0] KEY,
	input [17:0] SW,
	output [17:0] LEDR,
	
	output [6:0] HEX0,
	output [6:0] HEX1,
	output [6:0] HEX2,
	output [6:0] HEX3,
	
	output [17:0] SRAM_ADDR,
	inout [15:0] SRAM_DQ,
	output SRAM_WE_N, 
	output SRAM_OE_N, 
	output SRAM_UB_N,
	output SRAM_LB_N, 
	output SRAM_CE_N, 
	
	inout [35:0] GPIO_0
);
	
	// Serial -> SRAM Wishbone interface
	wire sram_wb_clk, sram_wb_cyc, sram_wb_stb, sram_wb_we, sram_wb_ack;
	wire [17:0] sram_wb_adr;
	wire [15:0] sram_wb_dat_io;
	wire [15:0] sram_wb_dat_oi;
	
	// Serial Wishbone interface and serial outputs
	wire wb_rst_o, wb_clk_o, wb_cyc_o, wb_stb_o, wb_we_o;
	assign LEDR = SW;
	
	sram sram0(
		.wb_clk_i( sram_wb_clk ),
		.wb_cyc_i( sram_wb_cyc ),
		.wb_stb_i( sram_wb_stb ),
		.wb_we_i( sram_wb_we ),
		.wb_ack_o( sram_wb_ack ),
	
		.wb_adr_i( sram_wb_adr ),
		.wb_dat_i( sram_wb_dat_io ),
		.wb_dat_o( sram_wb_dat_oi ),

		.sram_ce_n( SRAM_CE_N ),
		.sram_oe_n( SRAM_OE_N ),
		.sram_we_n( SRAM_WE_N ),
		.sram_lb_n( SRAM_LB_N ),
		.sram_ub_n( SRAM_UB_N ),

		.sram_data( SRAM_DQ ),
		.sram_addr( SRAM_ADDR ) );
	
	serial serial0(
		.wb_rst_i( wb_rst_o ),
		.wb_clk_i( wb_clk_o ),
		.wb_cyc_i( wb_cyc_o ),
		.wb_stb_i( wb_stb_o ),
		.wb_we_i( wb_we_o ),

		.sram_wb_clk_o( sram_wb_clk ),
		.sram_wb_cyc_o( sram_wb_cyc ),
		.sram_wb_stb_o( sram_wb_stb ),
		.sram_wb_we_o( sram_wb_we ),
		.sram_wb_ack_i( sram_wb_ack ),

		.sram_wb_adr_o( sram_wb_adr ),
		.sram_wb_dat_i( sram_wb_dat_oi ),

		.serial_clk_o( GPIO_0[0] ),
		.serial_cyc_o( GPIO_0[1] ),
		
		.serial_dat_o( GPIO_0[4:2] ),
		.serial_dat_i( GPIO_0[7:5] ),
		
		.hex_segs_o_0( HEX0 ),
		.hex_segs_o_1( HEX1 ),
		.hex_segs_o_2( HEX2 ),
		.hex_segs_o_3( HEX3 )
		
		 );
		
	assign wb_rst_o = SW[0];
	assign wb_clk_o = KEY[0];
	assign wb_cyc_o = 1'b1;
	assign wb_stb_o = SW[1];
	assign wb_we_o = 1'b1;
	
endmodule
