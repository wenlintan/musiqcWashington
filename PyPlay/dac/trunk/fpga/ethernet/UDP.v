
module UDP(
	input		wb_clk_i,
	input		wb_rst_i,
	
	input		wb_cyc_i,
	input 	wb_stb_i,
	input 	wb_we_i,
	output 	wb_ack_o,
	output	wb_rty_o,
	
	input [15:0]	wb_dat_i,
	output [15:0] 	wb_dat_o,
	
	// Non-wishbone UDP data
	input [31:0]	src_ip_i,
	input [31:0]	dest_ip_i,
	input [15:0]	dest_port_i,
	input [15:0]	length_i,
	
	output [31:0]			src_ip_o,
	output [31:0]			dest_ip_o,
	output reg [15:0]		dest_port_o,
	output reg [15:0]		length_o,
	
	// Wishbone master interface to IP
	output 	ip_wb_cyc_o,
	output	ip_wb_stb_o,
	output 	ip_wb_we_o,
	input		ip_wb_ack_i,
	input		ip_wb_rty_i,
	
	input [15:0]	ip_wb_dat_i,
	output [15:0]	ip_wb_dat_o,
	
	// Non-wishbone IP data
	input [31:0]	ip_src_ip_i,
	input [31:0]	ip_dest_ip_i,
	input [7:0]		ip_protocol_i,
	input [15:0]	ip_length_i,
	
	output [31:0]		ip_src_ip_o,
	output [31:0]		ip_dest_ip_o,
	output [7:0]		ip_protocol_o,
	output [15:0]		ip_length_o
	);
	
	localparam Idle = 3'b000;
	localparam WriteHeader = 3'b001;
	localparam Write = 3'b010;
	localparam ReadHeader = 3'b011;
	localparam Read = 3'b100;
	
	reg [9:0] word_counter;
	reg [2:0] state, next_state;
	
	always @(posedge wb_clk_i) begin
		if( wb_rst_i ) begin
			state <= Idle;
			word_counter <= 10'b0;
		end else begin
			state <= next_state;
			
			word_counter <= 
				(state == Idle)?	10'b0:
				(state == WriteHeader & ip_wb_ack_i)?		word_counter + 10'd1:
				(state == ReadHeader & ip_wb_ack_i)?		word_counter + 10'd1:
				word_counter;
		end
	end
	
	always @* begin
		next_state = state;
		
		case(state)
			Idle: begin
				if( wb_stb_i & wb_we_i )
					next_state = WriteHeader;
				else if( wb_stb_i )
					next_state = ReadHeader;
			end
			
			WriteHeader: begin
				if( ~wb_cyc_i | ip_wb_rty_i )
					next_state = Idle;
				else if( word_counter == 4 )
					next_state = Write;
			end
			
			Write: begin
				if( ~wb_cyc_i )
					next_state = Idle;
			end
			
			ReadHeader: begin
				if( ~wb_cyc_i | ip_wb_rty_i )
					next_state = Idle;
				else if( ip_wb_ack_i & (ip_protocol_i != 8'h11) )
					next_state = Idle;
				else if( word_counter == 4 )
					next_state = Read;
			end
			
			Read: begin
				if( ~wb_cyc_i | ip_wb_rty_i )
					next_state = Idle;
			end
		endcase
	end
	
	assign wb_ack_o =
		(state == Write)?				ip_wb_ack_i:
		(state == Read)?				ip_wb_ack_i:
		1'b0;
		
	assign wb_rty_o = 
		(state == ReadHeader)?		ip_wb_ack_i & (ip_protocol_i != 8'h11):
		ip_wb_rty_i;
		
	assign wb_dat_o = ip_wb_dat_i;
	
	assign ip_wb_cyc_o = (state != Idle);
	assign ip_wb_stb_o = ip_wb_cyc_o;
	
	assign ip_wb_we_o =
		(state == WriteHeader)?		1'b1:
		(state == Write)?				1'b1:
		1'b0;
		
	assign ip_wb_dat_o =
		(state == WriteHeader)?
			(word_counter == 0)?		dest_port_i:			// source port
			(word_counter == 1)?		dest_port_i:
			(word_counter == 2)?		length_i + 16'd8:
			(word_counter == 3)?		16'h0000:				// checksum
			16'h6162:
		(state == Write )?			wb_dat_i:
		16'h0000;
		
	assign ip_src_ip_o = src_ip_i;
	assign ip_dest_ip_o = dest_ip_i;
	assign ip_protocol_o = 8'h11;
	assign ip_length_o = length_i + 16'd8;
	
	assign src_ip_o = ip_src_ip_i;
	assign dest_ip_o = ip_dest_ip_i;
	always @(posedge wb_clk_i) begin
		if( (state == ReadHeader) & ip_wb_ack_i ) begin
			case(word_counter)
				10'd1:		dest_port_o <= {ip_wb_dat_i[7:0], ip_wb_dat_i[15:8]};
				10'd2:		length_o <= {ip_wb_dat_i[7:0], ip_wb_dat_i[15:8]} - 16'd8;
			endcase
		end
	end
			
	
endmodule
