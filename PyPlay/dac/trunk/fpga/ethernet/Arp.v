
module Arp(
	// Wishbone slave interface
	input 			wb_clk_i,
	input				wb_rst_i,
	
	input				wb_cyc_i,
	input				wb_stb_i,
	input				wb_we_i,
	output			wb_ack_o,
	output			wb_rty_o,
	
	// Non-wishbone ARP data
	input [31:0]	src_protocol_addr_i,
	input [31:0]	dest_protocol_addr_i,
	output [47:0]	dest_hardware_addr_o,
	
	// Wishbone master interface to ethernet
	output			enet_wb_cyc_o,
	output			enet_wb_stb_o,
	output			enet_wb_we_o,
	input [15:0]	enet_wb_dat_i,
	output [15:0]	enet_wb_dat_o,
	input				enet_wb_irq_i,
	input				enet_wb_ack_i,
	input				enet_wb_err_i
	);
	
	parameter src_hardware_addr = 48'h00_14_22_2c_2a_fd;
	
	localparam	Idle = 3'b000;
	localparam	Lookup = 3'b001;
	localparam	Write = 3'b010;
	localparam	Read = 3'b011;
	localparam	Store = 3'b100;
	localparam	Reply = 3'b101;
	
	reg [9:0] word_counter;
	reg [2:0] state, next_state;
	
	always @(posedge wb_clk_i) begin
		if( wb_rst_i ) begin
			state <= Idle;
			word_counter <= 10'b0;
		end else begin
			state <= next_state;
			
			word_counter <= 
				(state == Idle | state == Reply)?	10'b0:
				(state == Write && enet_wb_ack_i)?		word_counter + 10'd1:
				(state == Read && enet_wb_ack_i)?		word_counter + 10'd1:
				word_counter;
		end
	end
	
	always @* begin
		next_state = state;
		
		case(state)
			Idle: begin
				if( wb_stb_i && wb_we_i )
					next_state = Lookup;
				else if( wb_stb_i )
				//else if( enet_wb_irq_i )
					next_state = Read;
			end
			
			Lookup: begin
				if( lut_wb_ack_i )
					next_state = Idle;
				else if( lut_wb_err_i )
					next_state = Write;
			end
			
			Write: begin
				if( (word_counter == 21) | enet_wb_err_i )
					next_state = Idle;
			end
			
			Read: begin
				// If we are replying wait for error here to fully flush EnetIF pipe
				// We're going to immediately try to write to it
				if( enet_wb_err_i & op == 2'd1 & (tpa == src_protocol_addr_i) )
					next_state = Reply;
				else if( word_counter == 21 & op == 2'd2 )
					next_state = Store;
				else if( enet_wb_err_i )
					next_state = Idle;
			end
			
			Reply: begin
				next_state = Write;
			end
			
			Store: begin
				if( lut_wb_ack_i )
					next_state = Idle;
			end
		endcase
	end
		
	assign enet_wb_cyc_o = 
		(state == Write)?				1'b1:
		(state == Read)?				1'b1:
		1'b0;
		
	assign enet_wb_stb_o = 
		(state == Write)?				1'b1:
		(state == Read)?				1'b1:
		1'b0;
		
	assign enet_wb_we_o = 
		(state == Write)?				1'b1:
		(state == Read)?				1'b0:
		1'b0;
	
	assign enet_wb_dat_o = 
		(state == Write)?	
			(word_counter == 0)?			dest_hw[47:32]:
			(word_counter == 1)?			dest_hw[31:16]:
			(word_counter == 2)?			dest_hw[15:0]:			// Destination MAC address
		
			(word_counter == 3)?			src_hardware_addr[47:32]:
			(word_counter == 4)?			src_hardware_addr[31:16]:
			(word_counter == 5)?			src_hardware_addr[15:0]:		// Source MAC address
		
			(word_counter == 6)?			16'h0806:			// Ethertype ARP
		
			(word_counter == 7)?			16'h0001:			// Hardware type 1, ethernet
			(word_counter == 8)?			16'h0800:			// Protocol type 0x0800, ipv4
			(word_counter == 9)?			16'h0604:			// Hardware / Protocol address length
		
			(word_counter == 10)?		{14'h00, op}:		// Operation (1 request, 2, reply)
			(word_counter == 11)?		src_hardware_addr[47:32]:
			(word_counter == 12)?		src_hardware_addr[31:16]:
			(word_counter == 13)?		src_hardware_addr[15:0]:
			(word_counter == 14)?		src_protocol_addr_i[31:16]:
			(word_counter == 15)?		src_protocol_addr_i[15:0]:
			(word_counter == 16)?		sha[47:32]:
			(word_counter == 17)?		sha[31:16]:
			(word_counter == 18)?		sha[15:0]:
			(word_counter == 19)?		spa[31:16]:
			(word_counter == 20)?		spa[15:0]:
			16'b0:
		16'b0;
		
	reg [1:0] op;
	reg [31:0] spa, tpa;
	reg [47:0] dest_hw, sha;
	
	always @(posedge wb_clk_i) begin
		if( (state == Lookup) & lut_wb_err_i ) begin
			op <= 2'd1;										// Request
			dest_hw <= 48'hff_ff_ff_ff_ff_ff;		// Broadcast address
			sha <= 48'h00_00_00_00_00_00;
			spa <= dest_protocol_addr_i;
			
		end else if( (state == Read) & enet_wb_ack_i ) begin
			case( word_counter )
				10'd3:		op <= enet_wb_dat_i[9:8];
				
				10'd4:		sha[47:32] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd5:		sha[31:16] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd6:		sha[15:0] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd7:		spa[31:16] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd8:		spa[15:0] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				
				10'd12:		tpa[31:16] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd13:		tpa[15:0] 	<= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
			endcase
			
		end else if( (state == Reply) ) begin
			op <= 2'd2;										//Reply
			dest_hw <= sha;							
			// Other parameters still set from previous read
		end
	end
	
	// Wishbone master interface to lookup table
	wire lut_wb_cyc_o, lut_wb_stb_o, lut_wb_we_o, lut_wb_ack_i, lut_wb_err_i;
	wire [31:0] lut_protocol_addr;
	wire [47:0]	lut_hardware_addr_i, lut_hardware_addr_o;
	
	assign lut_wb_cyc_o = (state == Lookup) | (state == Store);
	assign lut_wb_stb_o = lut_wb_cyc_o;
	assign lut_wb_we_o = (state == Store);
	
	assign lut_protocol_addr = 
		(state == Lookup)?		dest_protocol_addr_i:		spa;
	assign lut_hardware_addr_i = sha;
	
	
	ArpLUT lut(
		.wb_clk_i( wb_clk_i ),
		.wb_rst_i( wb_rst_i ),
		.wb_cyc_i( lut_wb_cyc_o ),
		.wb_stb_i( lut_wb_stb_o ),
		.wb_we_i( lut_wb_we_o ),
		.wb_ack_o( lut_wb_ack_i ),
		.wb_err_o( lut_wb_err_i ),
		.arp_protocol_addr( lut_protocol_addr ),
		.arp_hardware_addr_i( lut_hardware_addr_i ),
		.arp_hardware_addr_o( lut_hardware_addr_o )
	);
		
	assign wb_ack_o =
		(state == Lookup)?			lut_wb_ack_i:
		(state == Read)?				enet_wb_err_i:
		(state == Store)?				lut_wb_ack_i:
		1'b0;
		
	assign wb_rty_o = 
		(state == Write)?				(word_counter == 21) | enet_wb_err_i:
		1'b0;
		
	assign dest_hardware_addr_o = lut_hardware_addr_o;
	
endmodule

module ArpLUT(
	// Wishbone slave interface
	input 			wb_clk_i,
	input				wb_rst_i,
	
	input				wb_cyc_i,
	input				wb_stb_i,
	input				wb_we_i,
	output			wb_ack_o,
	output			wb_err_o,
	
	// Non-wishbone ARP data
	input [31:0]	arp_protocol_addr,
	input [47:0]	arp_hardware_addr_i,
	output [47:0]	arp_hardware_addr_o
	);
	
	integer i;
	reg [2:0] index;
	reg found;
	
	reg [31:0] protocol_addrs[0:3];
	reg [47:0] hardware_addrs[0:3];
	
	always @(posedge wb_clk_i) begin
		if( wb_rst_i | ~wb_cyc_i | ~wb_stb_i ) begin
			index <= 3'b0;
			found <= 1'b0;
		end else begin
			if( protocol_addrs[0] == arp_protocol_addr ) begin
				found <= 1'b1;
				if( wb_we_i )	hardware_addrs[0] <= arp_hardware_addr_i;
			end else if( wb_we_i & (index == 3) ) begin
				found <= 1'b1;
				protocol_addrs[0] <= arp_protocol_addr;
				hardware_addrs[0] <= arp_hardware_addr_i;
			end else begin
				index <= index + 3'd1;
				
				for( i = 0; i < 4; i = i+1 ) begin
					protocol_addrs[ i ] <= protocol_addrs[ (i+1)%4 ];
					hardware_addrs[ i ] <= hardware_addrs[ (i+1)%4 ];
				end
			end
		end
	end
	
	assign arp_hardware_addr_o = hardware_addrs[0];
	assign wb_ack_o = found & wb_cyc_i & wb_stb_i;
	assign wb_err_o = ~found & (index == 4) & wb_cyc_i & wb_stb_i;	
	
endmodule
	