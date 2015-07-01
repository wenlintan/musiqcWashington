
module DAC(
	input wb_clk_i,
	input wb_rst_i,
	input wb_cyc_i,
	input wb_stb_i,
	input wb_we_i,

	// SRAM Wishbone interface
	output sram_wb_cyc_o,
	output sram_wb_stb_o,
	output sram_wb_we_o,
	input sram_wb_ack_i,

	output reg [SRAM_ADDRESS_WIDTH-1:0] sram_wb_adr_o,
	input [SRAM_DATA_WIDTH-1:0] sram_wb_dat_i,
	
	// DAC Chip serial interface
	output serial_clk_o,
	output serial_cyc_o,
	output [SERIAL_WIDTH-1:0] serial_dat_o
	//input [SERIAL_WIDTH-1:0] serial_dat_i

	);

	parameter SRAM_ADDRESS_WIDTH = 18;
	parameter SRAM_DATA_WIDTH = 16;

	parameter SERIAL_WIDTH = 3;
	parameter SERIAL_DATA_WIDTH = 5;
	parameter SERIAL_DATA_LENGTH = 24;
	parameter UPDATE_TIME = 2048;

	localparam IDLE = 3'b000;
	localparam READ_ADDR = 3'b001;
	localparam READ_DATA = 3'b010;
	localparam WRITE_SERIAL = 3'b011;
	localparam DELAY = 3'b100;

	reg [3:0] state, next_state;
	reg [1:0] chip_address, flags;
	reg [SERIAL_DATA_WIDTH-1:0] serial_counter;
	reg [SERIAL_DATA_LENGTH-1:0] serial_data;

	reg [15:0] update_counter;
	
	always @(posedge wb_clk_i)
	begin
		if( wb_rst_i ) begin
			state <= IDLE;
			sram_wb_adr_o <= 'b0;
			serial_counter <= 'b0;
			update_counter <= 'b0;
		end else if ( wb_cyc_i ) begin
			state <= next_state;
			
			serial_counter <= 
				(state == WRITE_SERIAL)?	serial_counter + 1:
				'b0;

			update_counter <=
				(state == IDLE)?													'b0:
				(state == DELAY && update_counter == UPDATE_TIME )?	'b0:
				update_counter + 1;
				
			sram_wb_adr_o <=
				(state == IDLE)?									'b0:
				(state == READ_ADDR && sram_wb_ack_i)?		sram_wb_adr_o + 1:
				(state == READ_DATA && sram_wb_ack_i)?		sram_wb_adr_o + 1:
				sram_wb_adr_o;
		end
		
	end
	
	always @(posedge wb_clk_i) begin
		if( state == READ_ADDR && sram_wb_ack_i ) begin
			flags <= sram_wb_dat_i[ 11: 10 ];
			chip_address <= sram_wb_dat_i[ 9: 8 ];
			serial_data[ SERIAL_DATA_LENGTH-1: 16 ] <= sram_wb_dat_i[ 7: 0 ];
		end if( state == READ_DATA && sram_wb_ack_i ) begin
			serial_data[ 15: 0 ] <= sram_wb_dat_i;
		end if( state == WRITE_SERIAL ) begin
			serial_data[ SERIAL_DATA_LENGTH-1: 0 ] <=
				{ serial_data[ SERIAL_DATA_LENGTH-2: 0 ], serial_data[SERIAL_DATA_LENGTH-1],  };
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
						next_state = READ_DATA;
					end
				end
				READ_DATA: begin
					if( sram_wb_ack_i ) begin
						next_state = WRITE_SERIAL;
					end
				end
				WRITE_SERIAL: begin
					if( serial_counter >= 5'd23 ) begin
						if( flags & 1 )
							next_state = IDLE;
						else if( flags & 2 )
							next_state = DELAY;
						else
							next_state = READ_ADDR;
					end
				end
				DELAY: begin
					if( update_counter == UPDATE_TIME ) begin
						next_state = READ_ADDR;
					end
				end
				default:
					next_state = IDLE;
			endcase		
		end		
	end

	assign sram_wb_cyc_o = (state == READ_ADDR || state == READ_DATA);
	assign sram_wb_stb_o = (state == READ_ADDR || state == READ_DATA);
	assign sram_wb_we_o = 1'b0;

	assign serial_clk_o = wb_clk_i;//(state == WRITE_SERIAL)? wb_clk_i: 1'b0;
	assign serial_cyc_o = ~(state == WRITE_SERIAL);
	assign serial_dat_o = 
		(state == WRITE_SERIAL && (chip_address == 3))? 
			{serial_data[SERIAL_DATA_LENGTH-1], serial_data[SERIAL_DATA_LENGTH-1], serial_data[SERIAL_DATA_LENGTH-1]}:
		(state == WRITE_SERIAL)? serial_data[SERIAL_DATA_LENGTH-1] << chip_address: 
		'b0;

endmodule
	






