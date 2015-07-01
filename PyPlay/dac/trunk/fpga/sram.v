
module sram(
	// External Wishbone interface
	input wb_clk_i,
	input wb_cyc_i,
	input wb_stb_i,
	input wb_we_i,
	output wb_ack_o,

	input [ADDRESS_WIDTH-1:0] wb_adr_i,
	input [DATA_WIDTH-1:0] wb_dat_i,
	output [DATA_WIDTH-1:0] wb_dat_o,

	// SRAM Interface
	output sram_ce_n,	// SRAM Chip Enable
	output sram_oe_n,	// SRAM Output Enable
	output sram_we_n,	// SRAM Write Enable
	output sram_lb_n,	// SRAM Lower-byte Control
	output sram_ub_n,	// SRAM Upper-byte Control

	inout [DATA_WIDTH-1:0] sram_data,
	output [ADDRESS_WIDTH-1:0] sram_addr
);

	parameter ADDRESS_WIDTH = 18;
	parameter DATA_WIDTH = 16;

	reg [1:0] read_ack_delay;

	assign sram_ce_n = !wb_cyc_i;
	assign sram_oe_n = !wb_stb_i;
	assign sram_we_n = !wb_stb_i;
	assign sram_lb_n = 1'b0;
	assign sram_ub_n = 1'b0;

	assign sram_data = (wb_we_i? wb_dat_i: 'bz);
	assign sram_addr = wb_adr_i;

	always @(posedge wb_clk_i)
	begin
		if( !wb_stb_i || !wb_cyc_i )
			read_ack_delay <= 2'b00;
		else begin
			read_ack_delay[1] <= !wb_we_i;
			read_ack_delay[0] <= read_ack_delay[1];
		end
	end

	assign wb_dat_o = (read_ack_delay[0]? sram_data: 'bz);
	assign wb_ack_o = wb_stb_i && (wb_we_i || read_ack_delay[0]);

endmodule


