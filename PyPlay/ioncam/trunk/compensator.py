
import math

from dac_control import DacController
from piezo_control import PiezoDriver
from gen_pot import DataFile
from ni_digital_io import NiDriver

from enthought.traits.api import Float, Int, String, Button, HasTraits
from enthought.traits.ui.api import View, Item, Group

class Compensator( HasTraits ):
    integration_frames = 30
    
    trap = String( "YTrap", label = "Trap Model" )
    driver = String( "UDP/192.168.1.101:4325", label = "DAC Controller Driver" )
    map_file = String( "trap_mappings.ods", label = "Trap-DAC Electrode Mapping File" )
    
    base_pot = String( "waveforms\\harmonic_rot_SNLY_20110318.csv", label = "Base Potential" )
    x_pot = String( "waveforms\\SNLY_compExTol_20110318.csv", label = "X Direction Compensation Potential" )
    y_pot = String( "waveforms\\SNLY_compEyTol_20110318.csv", label = "Y Direction Compensation Potential" )
    z_pot = String( "waveforms\\SNLY_compEzTol_20110318.csv", label = "Z Direction Compensation Potential" )
    emap = String( "_,[21-41]", label = "File-Trap Electrode Map" )
    
    base_scale = Float( 1.8, label = "Base Potential Scaling" )
    x_comp = Float( 0., label = "X Compensation (kV/m)" )
    y_comp = Float( 0., label = "Y Compensation (kV/m)" )
    z_comp = Float( 0., label = "Z Compensation (kV/m)" )
    
    current_step = Int( 0, label = "Current Output Step" )
    start_step = Int( 0, label = "Start Step for Compensation" )
    stop_step = Int( 10, label = "Stop Step for Compensation" )
    
    toggle_compensating = Button( "Toggle Compensating" )
    toggle_secular = Button( "Toggle Secular" )
    update_settings = Button( "Update Settings" )
    return_to_origin = Button( "Return To Origin" )
    
    view = View(    Group(  Item('trap'),
                            Item('driver'),
                            Item('map_file'),
                            
                            Item('base_pot'),
                            Item('x_pot'),
                            Item('y_pot'),
                            Item('z_pot'),
                            Item('emap'),
                            
                            Item('base_scale'),
                            Item('x_comp'),
                            Item('y_comp'),
                            Item('z_comp'),
                            
                            Item('current_step'),
                            Item('start_step'),
                            Item('stop_step'),
                            
                            Item('toggle_compensating'),
                            Item('toggle_secular'),
                            Item('update_settings'),
                            Item('return_to_origin'),
                            
                            label = "Compensation Settings",
                            show_border = True
                         )
                )
    
    def __init__( self ):        
        self.compensating = False
        self.initial_ion_pos = None
        self.secular = False
        self.comp_file = file( 'comp_test.txt', 'w' )
        self.set_step = 0
        
    def _update_dacs( self, out_step = None ):
        try:
            controller = DacController( self.trap, self.driver, self.map_file )
            emap = DataFile.build_electrode_map( self.emap )
            file = DataFile( self.base_pot, self.base_scale, emap ) 
        
            for dir, strength in zip( (self.x_pot, self.y_pot, self.z_pot), (self.x_comp, self.y_comp, self.z_comp) ):
                file.add_compensation( dir, strength, emap )
                
            if out_step is None:
                controller.update( file.potentials[ self.set_step ] )
                self.current_step = self.set_step
            else:
                step = 1
                if self.set_step > out_step:
                    if out_step != 0:
                        update = file.potentials[ self.set_step: out_step-1: -1 ]
                    else:
                        update = file.potentials[ self.set_step: out_step: -1 ]
                        update.append( file.potentials[ 0 ] )
                else:
                    update = file.potentials[ self.set_step: out_step+1 ]
                controller.multiple_update( update )
                self.current_step = out_step
        except ValueError:
            print "Failed to communicate with DACs"
        except:
            print "Unknown DAC problem"
            
        #piezo = PiezoDriver( 4, 9600 )
        #piezo.set_voltage( 0.75 * min( self.current_step / 25, 1.0 ) )
        
    def _control_secular( self, on ):
        driver = NiDriver( "Dev1/port0/line1" )
        driver.write_single( on )
        driver.close()
        self.secular = on
            
    def _return_to_origin_fired( self ):
        self._update_dacs( 0 )
        
    def _update_settings_fired( self ):
        self._update_dacs( self.current_step )
        
    def _toggle_secular_fired( self ):
        self._control_secular( not self.secular )

    def _toggle_compensating_fired( self ):
        self.compensating = not self.compensating
        print "Button", self.compensating
        if self.compensating:
            self._clear_updates()
            self.initial_pos = None

            self.x_comp = self.y_comp = self.z_comp = 0.
            self._update_dacs( self.start_step )
        
    def _average( self, ions ):
        ave_ions = []
        for ion in ions:
            if math.isnan( ion.x ) or math.isnan( ion.y ):
                continue

            found = None
            for i, aion in enumerate( ave_ions ):
                dx, dy = aion.x - ion.x, aion.y - ion.y
                if dx*dx + dy*dy < 16:
                    found = i
                    break
            if found is not None:
                aion = ave_ions[ found ]
                ave_ions[ found ].x = ( aion.x * aion.n + ion.x )/(aion.n + 1)
                ave_ions[ found ].y = ( aion.y * aion.n + ion.y )/(aion.n + 1)
                ave_ions[ found ].n += 1
            else:
                ion.n = 1
                ave_ions.append( ion )

        thresh = len(ions) / 6
        print "Average", ", ".join( "{0},{1}: {2}".format( i.x, i.y, i.n ) for i in ave_ions )
        ave_ions = [i for i in ave_ions if i.n >= thresh]
        return ave_ions
            
    def _compensate_y( self, ion, frame ):
        pass
        
    def _add_comp( self, delta ):
        if self.compensation_dir == 0:
            self.x_comp += delta
        elif self.compensation_dir == 1:
            self.z_comp += delta
            
    def _compensate_xz( self, ion, frame ):
        if self.initial_pos is None:
            if ion is None:
                return
                
            self.initial_pos = ion
            self.distance = 1e15
            self.step_size = [0.2, 0.2]
            self.compensation_dir = 0
            
            self._update_dacs( self.current_step )
            self._control_secular( True )
            self._clear_updates()
            
            print "Initial", self.initial_pos.x, self.initial_pos.y
            return
        
        if frame is None:
            return
            
        print "Considering", self.initial_pos.x, self.initial_pos.y
        distance = -frame[ int(self.initial_pos.y), int(self.initial_pos.x) ]
        print distance
        if distance < self.distance:
            self.distance = distance
            self.step_size[ self.compensation_dir ] *= 1.1
        else:
            self._add_comp( -self.step_size[ self.compensation_dir ] )
            self.step_size[ self.compensation_dir ] *= -0.9
        print "Update", self.x_comp, self.y_comp, self.z_comp, self.distance
            
        if all( abs(i) < 0.1 for i in self.step_size ):
            if self.current_step == self.stop_step:
                self.compensating = False
                
            self.comp_file.write( "{0}: {1}, {2}, {3}\n".format( 
                self.current_step, self.x_comp, self.y_comp, self.z_comp ) )
            self.comp_file.flush()
            
            self.initial_pos = None
            self._control_secular( False )
            self._update_dacs( self.current_step+1 )
            self._clear_updates()
        else:
            self.compensation_dir = (self.compensation_dir + 1)%2
            self._add_comp( self.step_size[ self.compensation_dir ] )
            self._update_dacs( self.current_step )
            
    def _clear_updates( self ):
        self.ions = []
        self.ion_frames = 0
        
        self.frame = None
        self.frames = 0

    def update_ions( self, ions ):
        if self.compensating:
            self.ions.extend( ions )
            self.ion_frames += 1
            
            if self.ion_frames > self.integration_frames:
                ions = self._average( self.ions )
                if len(ions) == 1:
                    self._compensate_xz( ions[0], None )
                    self.ion_frames = 0
                    self.ions = []

    def update_frame( self, frame ):
        if self.compensating:
            if self.frame is None: self.frame = frame.copy()
            self.frame += frame
            self.frames += 1
            
            if self.frames > self.integration_frames:
                self._compensate_xz( None, self.frame )
                self.frames = 0
                self.frame = None
