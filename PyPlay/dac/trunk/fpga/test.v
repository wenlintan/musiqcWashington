module test();

	// SRAM mock data
	reg [1:0] read_delay;
	reg [17:0] read_addr;
	wire [15:0] read_data;
	reg [15:0] test_data [0:1023];

	integer i;

	// Serial -> SRAM Wishbone interface
	wire sram_wb_clk, sram_wb_cyc, sram_wb_stb, sram_wb_we, sram_wb_ack;
	wire [17:0] sram_wb_adr;
	wire [15:0] sram_wb_dat_io;
	wire [15:0] sram_wb_dat_oi;

	// SRAM chip interface
	wire sram_ce_n, sram_oe_n, sram_we_n, sram_lb_n, sram_ub_n;
	wire [15:0] sram_data;
	wire [17:0] sram_addr;

	// Serial Wishbone interface and serial outputs
	reg wb_rst_o, wb_clk_o, wb_cyc_o, wb_stb_o, wb_we_o;
	wire serial_clk, serial_frame;
	wire [2:0] serial_dat_o;
	wire [2:0] serial_dat_i;

	sram sram0(
		.wb_clk_i( sram_wb_clk ),
		.wb_cyc_i( sram_wb_cyc ),
		.wb_stb_i( sram_wb_stb ),
		.wb_we_i( sram_wb_we ),
		.wb_ack_o( sram_wb_ack ),
	
		.wb_adr_i( sram_wb_adr ),
		.wb_dat_i( sram_wb_dat_io ),
		.wb_dat_o( sram_wb_dat_oi ),

		.sram_ce_n( sram_ce_n ),
		.sram_oe_n( sram_oe_n ),
		.sram_we_n( sram_we_n ),
		.sram_lb_n( sram_lb_n ),
		.sram_ub_n( sram_ub_n ),

		.sram_data( sram_data ),
		.sram_addr( sram_addr ) );
	
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

		.serial_clk_o( serial_clk ),
		.serial_cyc_o( serial_cyc ),
		
		.serial_dat_o( serial_dat_o ),
		.serial_dat_i( serial_dat_i ) );

	always @(posedge wb_clk_o)
	begin
		if( wb_rst_o || sram_ce_n || sram_oe_n )
			read_delay <= 'b0;
		else if( !sram_ce_n && !sram_oe_n ) begin
			read_delay[1] <= 1'b1;
			if( read_addr == sram_addr )
				read_delay[0] <= read_delay[1];
			else
				read_delay[0] <= 1'b0;
			read_addr <= sram_addr;
		end
	end

	assign read_data = test_data[ read_addr ];
	assign sram_data[15:8] = 
		(read_delay[0] && !sram_ub_n? read_data[15:8]: 'bz);
	assign sram_data[7:0] = 
		(read_delay[0] && !sram_lb_n? read_data[7:0]: 'bz);

	initial begin
		test_data[0] = 16'b0000_0000_0000_0000;
		test_data[1] = 16'b1111_1111_1111_1111;
		test_data[2] = 16'b0000_0000_0000_0000;
		test_data[3] = 16'b0000_0000_0000_0000;

		$display ("time\t clk cyc dat read_delay sram_data");
		$monitor ("%g\t %b %b %b %b %b %b", $time, 
			serial_clk, serial_cyc, serial_dat_o, 
			read_delay, sram_wb_ack, sram_wb_dat_oi );
		#10 wb_clk_o = 0;

		#10 wb_rst_o = 1;
		#10 wb_cyc_o = 0;
		#10 wb_stb_o = 0;
		#10 wb_we_o = 0;
		#10 wb_clk_o = 1;
		#10 wb_clk_o = 0;

		#10 wb_rst_o = 0;
		#10 wb_cyc_o = 1;
		#10 wb_stb_o = 1;
		#10 wb_clk_o = 1;
		#10 wb_clk_o = 0;

		#10 wb_stb_o = 0;
		#10 wb_clk_o = 1;
		#10 wb_clk_o = 0;
		for( i = 0; i < 50; i=i+1 ) begin
			#10 wb_clk_o = 1;
			#10 wb_clk_o = 0;
		end

		#10 $finish;
	end

endmodule

