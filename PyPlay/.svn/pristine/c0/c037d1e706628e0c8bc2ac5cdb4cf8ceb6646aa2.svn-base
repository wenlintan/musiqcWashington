
module Network(
	input 			wb_clk_i,
	input				wb_rst_i,
	input				wb_init_i,
	
	output reg		trigger_dac,
	
	// Wishbone master interface to SRAM
	output			sram_wb_cyc_o,
	output			sram_wb_stb_o,
	output			sram_wb_we_o,
	input				sram_wb_ack_i,	
	
	output [17:0]	sram_wb_adr_o,
	output [15:0]	sram_wb_dat_o,
	
	// Non-Wishbone ethernet DM9000A interface
	inout [15:0] 	ENET_DATA,
	output 			ENET_CMD,
	output 			ENET_CS_N,
	output 			ENET_WR_N,
	output 			ENET_RD_N,
	output 			ENET_RST_N,
	input 			ENET_INT,
	output 			ENET_CLK
	);
	
	localparam Idle = 3'b000;
	localparam Read = 3'b001;
	localparam Store1 = 3'b010;
	localparam Store2 = 3'b011;
	localparam Echo = 3'b100;
	
	reg [17:0]	address;
	reg [23:0] 	data;
	reg [1:0]	chip;
	reg [1:0]	flags;
	
	reg [9:0] word_counter;
	reg [2:0] state, next_state;
	
	always @(posedge wb_clk_i) begin
		if( wb_rst_i ) begin
			state <= Idle;
			word_counter <= 10'd0;
		end else begin
			state <= next_state;
			
			word_counter <= 
				(state == Idle | state == Store2)?					10'd0:
				((state == Read | state == Echo) & udp_ack)?		word_counter + 10'd1:
				word_counter;
		end
	end
	
	always @* begin
		next_state = state;
		
		case(state)
			Idle: begin
				if( ENET_INT )
					next_state = Read;
			end
			
			Read: begin
				if( (word_counter > 4 & ((length_o == 8) | (port_o == 4325))) & udp_rty ) begin
					next_state = Store1;
				end else if( udp_rty )
					next_state = Idle;
			end
			
			Store1: begin
				if( sram_wb_ack_i )
					next_state = Store2;
			end
			
			Store2: begin
				if( sram_wb_ack_i )
					next_state = Echo;
			end
			
			Echo: begin
				if( (word_counter == 4) | udp_rty )
					next_state = Idle;
			end
		endcase
	end
	
	// SRAM interface
	assign sram_wb_cyc_o = ((state == Store1) | (state == Store2));
	assign sram_wb_stb_o = ((state == Store1) | (state == Store2));
	assign sram_wb_we_o = 1'b1;
	
	assign sram_wb_adr_o = 
		(state == Store1)?	address:
		(state == Store2)?	{address[17:1], 1'b1}:
		18'h00000;
		
	assign sram_wb_dat_o =
		(state == Store1)?	{4'h0, flags, chip, data[23:16]}:
		(state == Store2)?	data[15:0]:
		16'h0000;
	
	// UDP interface
	wire udp_cyc, udp_stb, udp_we, udp_ack, udp_rty;
	wire [15:0] udp_dat_i, udp_dat_o;

	wire [31:0] src_ip_i, dest_ip_i, src_ip_o, dest_ip_o;
	wire [15:0] port_i, port_o;
	wire [15:0] length_i, length_o;
	
	assign udp_cyc = (state == Read) | (state == Echo);
	assign udp_stb = udp_cyc;
	assign udp_we = (state == Echo);
	
	assign src_ip_i = 32'hc0_a8_01_65;
	assign dest_ip_i = src_ip_o;
	assign port_i = port_o;
	assign length_i = 16'd0008;
	
	assign udp_dat_i = 
		(state == Echo)?
			(word_counter == 0)?		{14'h0000, address[17:16]}:
			(word_counter == 1)?		address[15:0]:
			(word_counter == 2)?		{3'h0, trigger_dac, flags, chip, data[23:16]}:
			(word_counter == 3)?		data[15:0]:
			16'h0000:
		16'h0000;
		
	always @(posedge wb_clk_i) begin
		if( state == Read ) begin
			case(word_counter)
				10'd0:				address[17:16] <= udp_dat_o[9:8];
				10'd1:				address[15:0] <= {udp_dat_o[7:0], udp_dat_o[15:8]};
				10'd2: begin
					trigger_dac <= udp_dat_o[4];
					flags <= udp_dat_o[3:2];
					chip <= udp_dat_o[1:0];
					data[23:16] <= udp_dat_o[15:8];
				end
				10'd3:				data[15:0] <= {udp_dat_o[7:0], udp_dat_o[15:8]};
			endcase
		end else if( state == Idle ) begin
			trigger_dac <= 1'b0;
		end
	end

	wire ip_cyc, ip_stb, ip_we, ip_ack, ip_rty;
	wire [15:0] ip_dat_i, ip_dat_o;

	wire [31:0] ip_src_ip_i, ip_dest_ip_i, ip_src_ip_o, ip_dest_ip_o;
	wire [7:0] ip_protocol_i, ip_protocol_o;
	wire [15:0] ip_length_i, ip_length_o;

UDP EthernetUDP(
	.wb_clk_i( wb_clk_i ),
	.wb_rst_i( wb_rst_i ),
	
	.wb_cyc_i( udp_cyc ),
	.wb_stb_i( udp_stb ),
	.wb_we_i( udp_we ),
	.wb_ack_o( udp_ack ),
	.wb_rty_o( udp_rty ),
	
	.wb_dat_i( udp_dat_i ),
	.wb_dat_o( udp_dat_o ),
	
	// Non-wishbone UDP data
	.src_ip_i( src_ip_i ),
	.dest_ip_i( dest_ip_i ),
	.dest_port_i( port_i ),
	.length_i( length_i ),
	
	.src_ip_o( src_ip_o ),
	.dest_ip_o( dest_ip_o ),
	.dest_port_o( port_o ),
	.length_o( length_o ),
	
	// Wishbone master interface to IP
	.ip_wb_cyc_o( ip_cyc ),
	.ip_wb_stb_o( ip_stb ),
	.ip_wb_we_o( ip_we ),
	.ip_wb_ack_i( ip_ack ),
	.ip_wb_rty_i( ip_rty ),
	
	.ip_wb_dat_i( ip_dat_o ),
	.ip_wb_dat_o( ip_dat_i ),
	
	// Non-wishbone IP data
	.ip_src_ip_i( ip_src_ip_o ),
	.ip_dest_ip_i( ip_dest_ip_o ),
	.ip_protocol_i( ip_protocol_o ),
	.ip_length_i( ip_length_o ),
	
	.ip_src_ip_o( ip_src_ip_i ),
	.ip_dest_ip_o( ip_dest_ip_i ),
	.ip_protocol_o( ip_protocol_i ),
	.ip_length_o( ip_length_i )
	);

IP EthernetIP(
	.wb_clk_i( wb_clk_i ),
	.wb_rst_i( wb_rst_i ),
	.wb_init_i( wb_init_i ),
	
	.wb_cyc_i( ip_cyc ),
	.wb_stb_i( ip_stb ),
	.wb_we_i( ip_we ),
	.wb_ack_o( ip_ack ),
	.wb_rty_o( ip_rty ),
	
	.wb_dat_i( ip_dat_i ),
	.wb_dat_o( ip_dat_o ),
	
	// Non-wishbone IP data
	.src_ip_i( ip_src_ip_i ),
	.dest_ip_i( ip_dest_ip_i ),
	.protocol_i( ip_protocol_i ),
	.length_i( ip_length_i ),
	
	.src_ip_o( ip_src_ip_o ),
	.dest_ip_o( ip_dest_ip_o ),
	.protocol_o( ip_protocol_o ),
	.length_o( ip_length_o ),
	
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

