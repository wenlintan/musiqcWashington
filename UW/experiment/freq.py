
import visa

class FreqDriver:
    def __init__( self, instr_name ):
        self.instr_name = instr_name
        self.instr = visa.instrument(instr_name)

    def set_frequency( self, freq, ampl ):
        "Set instrument frequency (MHz) and amplitude (Vpp)"
        command = "SWE:STAT ON;APPL:SIN {:.3f},{:.3f};".format( freq*1e6, ampl )
        self.instr.write( command )
        command = "FREQ:CENT {:.3f};".format( freq*1e6 )
        self.instr.write( command )
        command = "OUTP ON"
        self.instr.write( command )

class SRSDriver:
    def __init__( self, instr_name ):
        self.instr_name = instr_name
        self.instr = visa.instrument(instr_name)

    def set_frequency( self, freq, ampl=0 ):
        self.instr.write( "FREQ{}".format( freq * 1e6 ) )
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print( "usage: {} <freq> <ampl>".format( sys.argv[0] ) )
        sys.exit(0)
        
    #drv = FreqDriver( u'USB0::0x1AB1::0x0641::DG4B142100247::INSTR' )
    #drv.set_frequency( float(sys.argv[1]), float(sys.argv[2]) )
    drv = SRSDriver( u'ASRL1::INSTR' )
    drv.set_frequency( float(sys.argv[1]), float(sys.argv[2]) )
