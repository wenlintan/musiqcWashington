
import serial
import sys, argparse

class PiezoDriver:
    def __init__( self, port, baudrate ):
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial( port, baudrate )

    def set_voltage( self, v ):
        if v < 0. or v > 1.5:
            return
        self.serial.write( bytes('v') )
        self.serial.write( bytes( str(v) ) )
        self.serial.write( bytes( '\r' ) )

    def set_sweep( self, voltages ):
        print voltages
        self.serial.write( bytes('s') )
        self.serial.write( bytes( str(len(voltages)/2) + '\r' ) )

        for v, d in zip( voltages[::2], voltages[1::2] ):
            self.serial.write( bytes( str(v) + '\r' ) )
            self.serial.write( bytes( str(int(d)) + '\r' ) )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Controls a high voltage piezo driver")
    parser.add_argument('port', default = '0',
                        help="""COM port for communication with driver.""")
    parser.add_argument('baudrate', default = '9600',
                        help="""Baud rate for serial communication with driver.""")
    parser.add_argument('--voltage', required = False,
                        help="""Voltage to set piezo mirror to.""")
    parser.add_argument('--sweep', nargs = '+', type=float, required = False,
                        help="""Voltage and delay pairs to sweep through.
                        Example: 1. 300 1.2 500 outputs 100V for 300ms then
                          120V for 500ms then repeats."""
                        )

    args = vars(parser.parse_args())
    d = PiezoDriver( int(args['port']), int(args['baudrate']) )

    if args['voltage'] is not None:
        d.set_voltage( float(args['voltage']) )
    elif args['sweep'] is not None:
        d.set_sweep( args['sweep'] )
