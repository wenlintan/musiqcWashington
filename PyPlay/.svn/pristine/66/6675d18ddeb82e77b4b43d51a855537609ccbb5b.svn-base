module EthernetInit(
	input [4:0] address,
	input clock,
	output reg [17:0] q
	);

reg [17:0] memory[0:31];
initial $readmemh("ethernet_init_data.txt", memory);

always @(posedge clock) begin
	q <= memory[ address ];
end

endmodule
