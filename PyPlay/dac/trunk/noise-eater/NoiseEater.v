
module NoiseEater(
	input CLK,
	input RST,
	input HOLD,
	
	output ADC_RST,
	output reg ADC_CNVST,		// Falling edge begins conversion
	input ADC_EOC,		// Signals end of conversion
	
	output ADC_RD,
	output ADC_CS,
	input [15:0] ADC_DATA,
	
	output [15:0] DAC_DATA
	);
	
reg converting;
always @( posedge CLK ) begin
	if( !RST && !converting ) begin
		ADC_CNVST <= 1'b0;
		converting <= 1'b1;
	end else begin 
		converting <= 1'b0;
		ADC_CNVST <= 1'b1;
	end
end
	
reg latch_a, latch_b;
reg [15:0] data_a, data_b;

always @( posedge CLK ) begin
	if( !ADC_EOC ) begin
		latch_a <= latch_b;
		latch_b <= latch_a;
	end
end

reg [18:0] tmp_out, integral;
always @( posedge CLK ) begin
	if( RST ) begin
		tmp_out <= 16'b0;
		integral <= 16'b0;
	end else if( HOLD ) begin
		tmp_out <= tmp_out;
		integral <= 16'b0;
	end else begin
		integral <= integral + ( ADC_DATA - 16'b10 );
		tmp_out <= ( ADC_DATA - 16'b10 ) + integral;
	end
end

assign DAC_DATA = tmp_out[18: 3];

endmodule
