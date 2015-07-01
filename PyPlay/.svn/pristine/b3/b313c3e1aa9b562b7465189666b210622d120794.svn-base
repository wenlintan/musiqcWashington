
module EnetIF(  
  input 				wb_clk_i,
  input 				wb_rst_i,
  input 				wb_init_i,

  // Wishbone slave interface
  input				wb_cyc_i,
  input 				wb_stb_i,
  input				wb_we_i,
  input [15:0] 	wb_dat_i,
  output [15:0] 	wb_dat_o,
  output				wb_irq_o,
  output				wb_ack_o,
  output				wb_err_o,
  
  output				debug_data_latch,
  
  // Non-Wishbone ethernet DM9000A interface
  inout [15:0] 	ENET_DATA,
  output 			ENET_CMD,
  output 			ENET_CS_N,
  output 			ENET_WR_N,
  output 			ENET_RD_N,
  output 			ENET_RST_N,
  input 				ENET_INT,
  output 			ENET_CLK
  );

	assign      ENET_RST_N	= ~wb_rst_i;
	assign      ENET_CLK	= wb_clk_i;

	wire [17:0] init_rom_dat;

	localparam	Idle = 4'b0000;
	localparam	Init = 4'b0001;
	localparam	InitWriteReg = 4'b0010;
	localparam  TxInit = 4'b0101;
	localparam	TxWrite = 4'b0110;
	localparam	TxIssue = 4'b0111;
	localparam	IntHandle = 4'b1000;
	localparam	RxInit = 4'b1001;
	localparam	RxRead = 4'b1010;
	localparam 	RxClear = 4'b1011;
	localparam	RxFlush = 4'b1100;
	
	reg [3:0] state;
	always @(posedge wb_clk_i) begin
	
		if( wb_rst_i ) begin
			state <= Idle;
			command_counter_rst <= 1'b1;
		end else begin
		
			case( state )
				Idle: begin
					command_counter_rst <= 1'b1;
					if( wb_init_i )							state <= Init;
					else if( wb_stb_i & wb_we_i )			state <= TxInit;
					else if( wb_stb_i & ENET_INT )		state <= IntHandle;
					else											state <= Idle;
				end
				
				Init: begin
					command_counter_rst <= 1'b0;
					if( command_counter == 30 )			state <= Idle;
					else											state <= InitWriteReg;
				end

				InitWriteReg: begin
					command_counter_rst <= 1'b0;
					if( delay_counter == 300 )				state <= Init;
					else											state <= InitWriteReg;
				end

				TxInit: begin
					command_counter_rst <= 1'b1;
					if( ~wb_cyc_i )							state <= Idle;
					else if( delay_counter == 300 )		state <= TxWrite;
					else 											state <= TxInit;
				end

				TxWrite: begin
					command_counter_rst <= 1'b1;
					if( ~wb_cyc_i )							state <= TxIssue;
					else											state <= TxWrite;
				end
				
				TxIssue: begin
					command_counter_rst <= 1'b0;
					if( command_counter == 6 ) 			state <= Idle;
					else 											state <= TxIssue;
				end
				
				IntHandle: begin
					if( (command_counter == 1) & reg_done & wb_dat_o[0] ) begin
						state <= RxInit;
						command_counter_rst <= 1'b1;
					end else if( command_counter == 4 ) begin
						state <= Idle;
						command_counter_rst <= 1'b1;
					end else begin
						state <= IntHandle;
						command_counter_rst <= 1'b0;
					end
				end
				
				RxInit: begin
					command_counter_rst <= 1'b0;
					if( (command_counter == 4) & reg_done & ~wb_dat_o[0] ) begin
						//state <= Init;
						//command_counter_rst <= 1'b1;
						state <= RxFlush;
					end else if( command_counter == 8 ) state <= RxRead;
					else 											state <= RxInit;
				end
				
				RxRead: begin
					command_counter_rst <= 1'b1;
					if( word_counter == 0 )					state <= RxInit; //state <= RxFlush;
					else											state <= RxRead;
				end
				
				RxFlush: begin
					if( ~wb_cyc_i )							state <= Idle;
					else											state <= RxFlush;
				end
			endcase
			
		end
	end

	reg command_counter_rst;
	reg [4:0] command_counter;
	reg [9:0] delay_counter;
	reg [15:0] word_counter;
	
	always @(posedge wb_clk_i) begin
		if( wb_rst_i ) begin
			delay_counter <= 10'd0;
			word_counter <= 8'd0;
			command_counter <= 4'd0;
		end else begin
			delay_counter <= 
				(state == Idle)? 						10'd0: 
				(state == Init)? 						10'd0: 
				(delay_counter == 300)?				10'd0:
				(delay_counter + 10'd1);

			word_counter <= 
				(state == TxInit)? 									16'd0: 
				(state == TxWrite & reg_done)?					word_counter + 16'd2:
				(state == RxInit & reg_done & (command_counter == 7))?	wb_dat_o:
				(state == RxRead & reg_done && (word_counter == 1))?		16'd0:
				(state == RxRead & reg_done)?						word_counter - 16'd2:
				word_counter;
			
			command_counter <=
				(command_counter_rst)?			4'd0:
				reg_done?							command_counter + 4'd1:
				command_counter;
		end
	end
	
	wire reg_start, reg_we, reg_addr, reg_done;
	wire [15:0] reg_data;

	reg [2:0] reg_delay;
	always @(posedge wb_clk_i) begin
		reg_delay[2] <= reg_done;
		reg_delay[1] <= reg_delay[2];
		reg_delay[0] <= reg_delay[1];
	end
	
	assign wb_dat_o =			ENET_DATA;
	assign wb_irq_o = 		ENET_INT;
	
	assign wb_ack_o = 
		(state == TxWrite)?	reg_delay[2]:
		(state == RxRead)?	reg_done:
		1'b0;
		
	assign wb_err_o =
		(state == IntHandle)?	command_counter[2]:
		(state == TxIssue)?		wb_stb_i:
		(state == RxFlush)?		wb_stb_i:
		1'b0;
		
	assign debug_data_latch = 
		//(state == IntHandle)?	((command_counter == 1) && reg_done):
		(state == RxInit)?	((command_counter == 4) && reg_done):
		1'b0;
	
	assign reg_start = 
		(state == InitWriteReg)?	delay_counter == 0:
		(state == TxInit)?			delay_counter == 0:
		(state == TxWrite)?			delay_counter == 0:
		(state == TxIssue)?			delay_counter == 0:
		(state == IntHandle)?
			(command_counter == 1)?	reg_delay[1]:
			delay_counter == 0:
		(state == RxInit)?	
			(command_counter == 3)?	reg_delay[1]:
			(command_counter == 4)?	reg_delay[1]:
			(command_counter == 6)?	reg_delay[1]:
			(command_counter == 7)?	reg_delay[1]:
			delay_counter == 0:
		(state == RxRead)?			reg_delay[1]:
		1'b0;
		
	assign reg_we = 
		(state == InitWriteReg)? 	init_rom_dat[8]:
		(state == TxInit)?			1'b1:
		(state == TxWrite)?			1'b1:
		(state == TxIssue)?			1'b1:
		(state == IntHandle)?
			(command_counter == 0)?		1'b1:
			(command_counter == 2)?		1'b1:
			(command_counter == 3)?		1'b1:
			1'b0:
		(state == RxInit)?
			(command_counter == 0)?		1'b1:
			(command_counter == 1)?		1'b1:
			(command_counter == 2)?		1'b1:
			(command_counter == 5)?		1'b1:
			1'b0:
		(state == RxRead)?				1'b0:
		1'b0;
		
	assign reg_addr = 
		(state == InitWriteReg)?	init_rom_dat[9]:
		(state == TxInit)?			1'b0:
		(state == TxWrite)?			1'b1:
		(state == TxIssue)?
			(command_counter == 0)?		1'b0:
			(command_counter == 1)?		1'b1:
			(command_counter == 2)?		1'b0:
			(command_counter == 3)?		1'b1:
			(command_counter == 4)?		1'b0:
			(command_counter == 5)?		1'b1:
			1'b0:
		(state == IntHandle)?
			(command_counter == 0)?		1'b0:
			(command_counter == 2)?		1'b0:
			1'b1:
		(state == RxInit)?
			(command_counter == 0)?		1'b0:
			(command_counter == 2)?		1'b0:
			(command_counter == 5)?		1'b0:
			1'b1:
		(state == RxRead)?			1'b1:
		1'b0;
		
	assign reg_data = 
		(state == InitWriteReg)? 	{8'b0, init_rom_dat[7:0]}:
		(state == TxInit)?			16'h00f8:
		(state == TxWrite)?			{wb_dat_i[7:0], wb_dat_i[15:8]}:
		(state == TxIssue)?
			(command_counter == 0)?		16'h00fd:
			(command_counter == 1)?		{8'h00, 8'h00}:
			(command_counter == 2)?		16'h00fc:
			(command_counter == 3)?		word_counter:
			(command_counter == 4)?		16'h0002:
			(command_counter == 5)?		16'h0001:
			16'h0000:
		(state == IntHandle)?
			(command_counter == 0)?		16'h00fe:
			(command_counter == 2)?		16'h00fe:
			(command_counter == 3)?		16'h003f:
			16'h0000:
		(state == RxInit)?
			(command_counter == 0)?		16'h00fe:
			(command_counter == 1)?		16'h0001:
			(command_counter == 2)?		16'h00f0:
			(command_counter == 5)?		16'h00f2:
			16'h0000:
		16'h0000;

	localparam	RegIdle = 3'b000;
	localparam 	RegSetup = 3'b001;
	localparam	RegIssue = 3'b010;
	localparam	RegHold0 = 3'b011;
	localparam	RegHold1 = 3'b100;

	reg [2:0] reg_state, reg_next_state;
	always @(posedge wb_clk_i) begin
		if( wb_rst_i ) 	reg_state <= RegIdle;
		else					reg_state <= reg_next_state;
	end

	always @* begin
		case (reg_state)
			RegIdle: begin
				reg_next_state = RegIdle;
				if( reg_start )
					reg_next_state = RegSetup;
			end

			RegSetup:		reg_next_state = RegIssue;
			RegIssue:		reg_next_state = RegHold0;
			RegHold0:		reg_next_state = RegHold1;
			RegHold1:		reg_next_state = RegIdle;
		endcase
	end
	
	EthernetInit EnetInitRom(
		.address(command_counter),
		.clock(wb_clk_i),
		.q(init_rom_dat)
	);
	
	assign ENET_DATA = (~reg_we && reg_state != RegIdle)? 16'bz: reg_data;
	assign ENET_CMD = (reg_state == RegIdle)? 1'b0: reg_addr;
	assign ENET_CS_N = 1'b0;
	assign ENET_WR_N = (reg_state == RegIssue)? ~reg_we: 1'b1;
	assign ENET_RD_N = (reg_state == RegIssue)? reg_we : 1'b1;

	assign reg_done = (reg_state == RegHold1);
	
endmodule
