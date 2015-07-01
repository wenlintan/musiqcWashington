
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

module serial(
	input wb_rst_i,
	input wb_clk_i,
	input wb_cyc_i,
	input wb_stb_i,
	input wb_we_i,

	// SRAM Wishbone interface
	output sram_wb_clk_o,
	output sram_wb_cyc_o,
	output sram_wb_stb_o,
	output sram_wb_we_o,
	input sram_wb_ack_i,

	output reg [SRAM_ADDRESS_WIDTH-1:0] sram_wb_adr_o,
	input [SRAM_DATA_WIDTH-1:0] sram_wb_dat_i,
	
	// DAC Chip serial interface
	output serial_clk_o,
	output serial_cyc_o,
	output [SERIAL_WIDTH-1:0] serial_dat_o,
	input [SERIAL_WIDTH-1:0] serial_dat_i,
	
	// HEX Output
	output [6:0] hex_segs_o_0,
	output [6:0] hex_segs_o_1,
	output [6:0] hex_segs_o_2,
	output [6:0] hex_segs_o_3

	);

	parameter SRAM_ADDRESS_WIDTH = 18;
	parameter SRAM_DATA_WIDTH = 16;

	parameter SERIAL_WIDTH = 3;
	parameter SERIAL_DATA_WIDTH = 5;

	parameter SERIAL_DATA_LENGTH = 24;
	parameter SERIAL_GROUP_START = 19;
	parameter SERIAL_CHANNEL_START = 16;
	parameter SERIAL_VOLTAGE_START = 0;

	localparam IDLE = 3'b000;
	localparam READ_ADDR = 3'b001;
	localparam STORE_ADDR = 3'b010;
	localparam READ_DATA = 3'b011;
	localparam STORE_DATA = 3'b100;
	localparam WRITE_SERIAL = 3'b101;

	reg [3:0] state, next_state;
	reg [SERIAL_WIDTH-1:0] chip_address;
	reg [SERIAL_DATA_WIDTH-1:0] serial_index;
	reg [SERIAL_DATA_LENGTH-1:0] serial_data;
	
	reg [3:0] hex0, hex1, hex2, hex3;
	HexDigit hex_digit0( hex_segs_o_0, hex0 );
	HexDigit hex_digit1( hex_segs_o_1, hex1 );
	HexDigit hex_digit2( hex_segs_o_2, hex2 );
	HexDigit hex_digit3( hex_segs_o_3, hex3 );
	
	always @(posedge wb_clk_i)
	begin
		if( wb_rst_i ) begin
			state <= IDLE;
			sram_wb_adr_o <= 'b0;
			hex0 <= 'hd;
			hex1 <= 'he;
			hex2 <= 'ha;
			hex3 <= 'hd;
		end else if ( wb_cyc_i ) begin
			state <= next_state;
			case( next_state )
				STORE_ADDR: begin
					chip_address <= sram_wb_dat_i[ 7: 5 ];
					serial_data[ SERIAL_DATA_LENGTH-1: SERIAL_GROUP_START ] 
						<= sram_wb_dat_i[4:3] + 1;
					serial_data[ SERIAL_GROUP_START-1: SERIAL_CHANNEL_START ] 
						<= sram_wb_dat_i[2:0];

					hex0 <= sram_wb_dat_i[15:12];
					hex1 <= sram_wb_dat_i[11:8];
					hex2 <= sram_wb_dat_i[7:4];
					hex3 <= sram_wb_dat_i[3:0];
					sram_wb_adr_o <= sram_wb_adr_o + 1;
				end 
				STORE_DATA: begin
					serial_data[ SERIAL_CHANNEL_START-1: 0 ] <= sram_wb_dat_i;
					hex0 <= sram_wb_dat_i[15:12];
					hex1 <= sram_wb_dat_i[11:8];
					hex2 <= sram_wb_dat_i[7:4];
					hex3 <= sram_wb_dat_i[3:0];
					sram_wb_adr_o <= sram_wb_adr_o + 1;
					serial_index <= 'b0;
				end
				WRITE_SERIAL: begin
					hex0 <= serial_data[ serial_index ] << chip_address;
					hex3 <= serial_index[4];
					hex2 <= serial_index[3:0];
					serial_index <= serial_index + 1;
				end
			endcase		
		end
	end

	always @(*)
	begin
		next_state = state;
		if( wb_cyc_i ) begin
			case( state )
				IDLE: begin
					if( wb_stb_i ) begin
						next_state = READ_ADDR;
					end
				end
				READ_ADDR: begin
					if( sram_wb_ack_i ) begin
						next_state = STORE_ADDR;
					end
				end
				STORE_ADDR:
					next_state = READ_DATA;
				READ_DATA: begin
					if( sram_wb_ack_i ) begin
						next_state = STORE_DATA;
					end
				end
				STORE_DATA:
					next_state = WRITE_SERIAL;
				WRITE_SERIAL: begin
					if( serial_index >= 5'd23 ) begin
						next_state = IDLE;
					end
				end
				default:
					next_state = IDLE;
			endcase		
		end		
	end

	assign sram_wb_clk_o = wb_clk_i;
	assign sram_wb_cyc_o = (state == READ_ADDR || state == READ_DATA);
	assign sram_wb_stb_o = (state == READ_ADDR || state == READ_DATA);
	assign sram_wb_we_o = 1'b0;

	assign serial_clk_o = wb_clk_i;
	assign serial_cyc_o = (state == WRITE_SERIAL);
	assign serial_dat_o = 
		(state == WRITE_SERIAL? 
			serial_data[ serial_index ] << chip_address: 
			'b0);

endmodule
	






