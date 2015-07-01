

module IP(
	// Wishbone slave interface
	input				wb_clk_i,
	input				wb_rst_i,
	input				wb_init_i,
	
	input				wb_cyc_i,
	input				wb_stb_i,
	input				wb_we_i,
	output			wb_ack_o,
	output			wb_rty_o,
	
	input [15:0]	wb_dat_i,
	output [15:0]	wb_dat_o,
	
	// Non-wishbone IP data
	input [31:0]	src_ip_i,
	input [31:0]	dest_ip_i,
	input [7:0]		protocol_i,
	input [15:0]	length_i,
	
	output reg [31:0]		src_ip_o,
	output reg [31:0]		dest_ip_o,
	output reg [7:0]		protocol_o,
	output reg [15:0]		length_o,
	
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
	
	localparam	Idle = 3'b000;
	localparam	ArpLookup = 3'b001;
	localparam	WriteHeader = 3'b010;
	localparam	Write = 3'b011;
	localparam	ReadType = 3'b100;
	localparam	ReadHeader = 3'b101;
	localparam	Read = 3'b110;
	
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
				(state == WriteHeader && enet_wb_ack_i)?		word_counter + 10'd1:
				(state == ReadType && enet_wb_ack_i)?			word_counter + 10'd1:
				(state == ReadHeader && enet_wb_ack_i)?		word_counter + 10'd1:
				word_counter;
		end
	end
	
	always @* begin
		next_state = state;
		
		case(state)
			Idle: begin
				if( wb_stb_i && wb_we_i )
					next_state = ArpLookup;
				else if( wb_stb_i )
					next_state = ReadType;
			end
			
			ArpLookup: begin
				if( ~wb_cyc_i | arp_wb_rty_i )
					next_state = Idle;
				if( arp_wb_ack_i )
					next_state = WriteHeader;
			end
			
			WriteHeader: begin
				if( ~wb_cyc_i )
					next_state = Idle;
				else if( word_counter == 17 )
					next_state = Write;
			end
			
			Write: begin
				if( ~wb_cyc_i )
					next_state = Idle;
			end
			
			ReadType: begin
				if( ~wb_cyc_i | enet_wb_err_i )
					next_state = Idle;
				else if( (word_counter == 7) & (ethertype == 16'h0806) ) begin
					if( arp_wb_ack_i | arp_wb_rty_i )
						next_state = Idle;
				end else if( (word_counter == 7) & (ethertype == 16'h0800) )
					next_state = ReadHeader;
				else if( (word_counter == 7) )
					next_state = Idle;
			end
			
			ReadHeader: begin
				if( word_counter == 17 )
					next_state = Read;
			end
			
			Read: begin
				if( ~wb_cyc_i | enet_wb_err_i )
					next_state = Idle;
			end
		endcase
	end
	
	assign wb_dat_o = enet_wb_dat_i;
	assign wb_ack_o = 
		(state == Write)?				enet_wb_ack_i:
		(state == Read)?				enet_wb_ack_i:
		1'b0;
		
	assign wb_rty_o =
		(state == ArpLookup)?		arp_wb_rty_i:
		(state == ReadType)?			enet_wb_err_i:
		(state == ReadHeader)?		enet_wb_err_i:
		(state == Read)?				enet_wb_err_i:
		1'b0;
		
	assign enet_wb_cyc_o = 
		(state == WriteHeader)?		1'b1:
		(state == Write)?				1'b1:
		(state == ReadType)?			1'b1:
		(state == ReadHeader)?		1'b1:
		(state == Read)?				1'b1:
		1'b0;
		
	assign enet_wb_stb_o = 
		(state == WriteHeader)?		1'b1:
		(state == Write)?				1'b1:
		(state == ReadType)?			(word_counter < 7):
		(state == ReadHeader)?		1'b1:
		(state == Read)?				1'b1:
		1'b0;
		
	assign enet_wb_we_o = 
		(state == WriteHeader)?		1'b1:
		(state == Write)?				1'b1:
		(state == ReadType)?			1'b0:
		(state == ReadHeader)?		1'b0:
		(state == Read)?				1'b0:
		1'b0;
	
	assign enet_wb_dat_o = 
		(state == WriteHeader)?	
			(word_counter == 0)?			arp_hardware_addr_i[47:32]:
			(word_counter == 1)?			arp_hardware_addr_i[31:16]:
			(word_counter == 2)?			arp_hardware_addr_i[15:0]:	// Destination MAC address
			
			(word_counter == 3)?			16'h0014:
			(word_counter == 4)?			16'h222c:
			(word_counter == 5)?			16'h2afd:				// Source MAC address
			
			(word_counter == 6)?			16'h0800:				// IPv4 Ethertype
			
			(word_counter == 7)?			16'h4500:				// IPv4, no header options, other crap
			(word_counter == 8)?			length_i + 16'd20:	// length including header
			(word_counter == 9)?			16'h0000:				// identification?
			(word_counter == 10)?		16'h4000:				// fragment stuff (don't fragment)
			(word_counter == 11)?		{8'h40, protocol_i}:	// ttl, protocol
			(word_counter == 12)?		16'h0000:				// checksum
			(word_counter == 13)?		src_ip_i[31:16]:
			(word_counter == 14)?		src_ip_i[15:0]:		// source ip
			(word_counter == 15)?		dest_ip_i[31:16]:
			(word_counter == 16)?		dest_ip_i[15:0]:		// destination ip
			16'h6161:
		(state == Write)?					wb_dat_i:
		16'h0000;			
		
	assign arp_wb_cyc_o =
		(state == ArpLookup)?			1'b1:
		(state == ReadType)?				(word_counter == 7) & (ethertype == 16'h0806):
		1'b0;
		
	assign arp_wb_stb_o = arp_wb_cyc_o;
	
	assign arp_wb_we_o =
		(state == ArpLookup)?			1'b1:
		(state == ReadType)?				1'b0:
		1'b0;
		
	assign arp_src_protocol_addr = src_ip_i;
	assign arp_dest_protocol_addr = dest_ip_i;
	
	reg [15:0] ethertype, length;
	
	always @(posedge wb_clk_i) begin
		if( ((state == ReadType) | (state == ReadHeader)) & enet_wb_ack_i ) begin
			case( word_counter )					
				10'd6:		ethertype <= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd8:		length_o <= {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]} - 16'd20;
				10'd11:		protocol_o <= enet_wb_dat_i[15:8];
				10'd13:		src_ip_o[31:16] <=  {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd14:		src_ip_o[15:0] <=  {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd15:		dest_ip_o[31:16] <=  {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};
				10'd16:		dest_ip_o[15:0] <=  {enet_wb_dat_i[7:0], enet_wb_dat_i[15:8]};				
			endcase
		end
	end
	
	// Wishbone master interface to EnetIF
	wire enet_wb_cyc_o, enet_wb_stb_o, enet_wb_we_o;
	wire enet_wb_irq_i, enet_wb_ack_i, enet_wb_err_i;
	wire [15:0] enet_wb_dat_o, enet_wb_dat_i;
		
	// Wishbone master interface to ARP
	wire arp_wb_cyc_o, arp_wb_stb_o, arp_wb_we_o, arp_wb_ack_i, arp_wb_rty_i;
	wire [31:0]	arp_src_protocol_addr, arp_dest_protocol_addr;
	wire [47:0]	arp_hardware_addr_i;
	
	// Wishbone master ARP interface to EnetIF
	wire arp_enet_wb_cyc_o, arp_enet_wb_stb_o, arp_enet_wb_we_o;
	wire arp_enet_wb_irq_i, arp_enet_wb_ack_i, arp_enet_wb_err_i;
	wire [15:0] arp_enet_wb_dat_o, arp_enet_wb_dat_i;
	
	// Wishbone master arbiter interface to EnetIF
	wire enet_cyc, enet_stb, enet_we;
	wire enet_irq, enet_ack, enet_err;
	wire [15:0] enet_dat_o, enet_dat_i;
	
	assign enet_cyc = 	arp_enet_wb_cyc_o? arp_enet_wb_cyc_o: enet_wb_cyc_o;
	assign enet_stb = 	arp_enet_wb_cyc_o? arp_enet_wb_stb_o: enet_wb_stb_o;
	assign enet_we = 		arp_enet_wb_cyc_o? arp_enet_wb_we_o: enet_wb_we_o;
	assign enet_dat_o = 	arp_enet_wb_cyc_o? arp_enet_wb_dat_o: enet_wb_dat_o;
	
	assign enet_wb_dat_i =	~arp_enet_wb_cyc_o? enet_dat_i: 16'h0000;
	assign enet_wb_irq_i = 	~arp_enet_wb_cyc_o & enet_irq;
	assign enet_wb_ack_i = 	~arp_enet_wb_cyc_o & enet_ack;
	assign enet_wb_err_i =	~arp_enet_wb_cyc_o & enet_err;
	
	assign arp_enet_wb_dat_i =	arp_enet_wb_cyc_o? enet_dat_i: 16'h0000;
	assign arp_enet_wb_irq_i =	arp_enet_wb_cyc_o & enet_irq;
	assign arp_enet_wb_ack_i =	arp_enet_wb_cyc_o & enet_ack;
	assign arp_enet_wb_err_i =	arp_enet_wb_cyc_o & enet_err;

	
Arp EthernetArp(
	.wb_clk_i( wb_clk_i ),
	.wb_rst_i( wb_rst_i ),
	
	.wb_cyc_i( arp_wb_cyc_o ),
	.wb_stb_i( arp_wb_stb_o ),
	.wb_we_i( arp_wb_we_o ),
	.wb_ack_o( arp_wb_ack_i ),
	.wb_rty_o( arp_wb_rty_i ),
	
	// Non-wishbone ARP data
	.src_protocol_addr_i( arp_src_protocol_addr ),
	.dest_protocol_addr_i( arp_dest_protocol_addr ),
	.dest_hardware_addr_o( arp_hardware_addr_i ),
	
	.enet_wb_cyc_o( arp_enet_wb_cyc_o ),
	.enet_wb_stb_o( arp_enet_wb_stb_o ),
	.enet_wb_we_o( arp_enet_wb_we_o ),
	.enet_wb_dat_i( arp_enet_wb_dat_i ),
	.enet_wb_dat_o( arp_enet_wb_dat_o ),
	.enet_wb_irq_i( arp_enet_wb_irq_i ),
	.enet_wb_ack_i( arp_enet_wb_ack_i ),
	.enet_wb_err_i( arp_enet_wb_err_i )
	);

EnetIF EthernetInterface(
  .wb_clk_i( wb_clk_i ),
  .wb_rst_i( wb_rst_i ),
  .wb_init_i( wb_init_i ),
  
  .wb_cyc_i( enet_cyc ),
  .wb_stb_i( enet_stb ),
  .wb_we_i( enet_we ),
  .wb_dat_i( enet_dat_o ),
  .wb_dat_o( enet_dat_i ),
  .wb_irq_o( enet_irq ),
  .wb_ack_o( enet_ack ),
  .wb_err_o( enet_err ),
  
  .ENET_DATA(ENET_DATA),
  .ENET_CMD(ENET_CMD),
  .ENET_CS_N(ENET_CS_N),
  .ENET_WR_N(ENET_WR_N),
  .ENET_RD_N(ENET_RD_N),
  .ENET_RST_N(ENET_RST_N),
  .ENET_INT(ENET_INT),
  .ENET_CLK(ENET_CLK)
  );
	
endmodule
	
	