
module RoundRobinArbiter(
	input			wb_clk_i,
	input			wb_rst_i,
	
	input	[nMasters-1:0]		master_wb_cyc_i,
	output [nMasters-1:0]	master_wb_gnt_o
	
	);
	
	parameter	nMasters = 2;
	
	
endmodule
