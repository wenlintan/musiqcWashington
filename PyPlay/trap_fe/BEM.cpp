
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

#include "BEMSolver.hpp"

void load_trap( const std::string& filename, BEMSolver& solver,
    std::vector<size_t>& rf_geoms, std::vector<size_t>& dc_geoms ) {

	std::ifstream input( filename.c_str() );
	std::string label, name;
	while( input >> label ) {
		input >> name;
		std::cout << "Loading electrode: " << name << std::endl;
		BEMGeometry* geom = new BEMGeometry();
		input >> *geom;

		size_t index = solver.add_geometry( geom );
		if( name == "RF" ) {
			rf_geoms.push_back( index );
		} else {
			dc_geoms.push_back( index );
		}
	}
}

void create_ion_trap( BEMSolver& solver ) {
    // Create 4 rods that form rf trap
    Real rod_offsets[][3] = {
        { -500., -500., 0. }, { -500., 500., 0. },
        { 500., -500., 0. }, { 500., 500., 0. } };
    for( size_t r = 0; r < 4; ++r ) {
        BEMGeometry* rod = BEMGeometry::create_cyl( 
            0., 200., -20000., 20000., 
            rod_offsets[r], 80, 3, 30 );
        rod->voltage = 0.;
        solver.add_geometry( rod );
    }

    // Create washers on either end around all of the rods
    // for axial confinement
    Real washer_offsets[][3] = {
        { 0., 0., -15000 }, { 0., 0., 15000. } 
        };
    for( size_t w = 0; w < 2; ++w ) {
        BEMGeometry* washer = BEMGeometry::create_cyl( 
            1000., 3000., -1000., 1000.,
            washer_offsets[w], 30, 30, 30 );
        washer->voltage = 1.0;
        solver.add_geometry( washer );
    }
}

void create_chip_trap( BEMSolver& solver,
    std::vector<size_t>& rf_geoms, std::vector<size_t>& dc_geoms ) {
    Real spacing = 5.;
    Real inner_ground_depth = -4.5;
    Real inner_ground_height = 100.;
    Real inner_ground_offset = 30.;
    Real dc_depth = -4.5, dc_width = 64., dc_height = 20., dc_spacing = 1.;
    Real gap_height = 60.;
    Real rf_height = 95.;
    Real ground_height = 500.;

    // Create outer ground rails
    Real ground_rail_offsets[][3] = {
        { 0., -gap_height / 2 - dc_height - rf_height - ground_height -
            spacing * 2., 0. },
        { 0., gap_height / 2 + dc_height + rf_height + spacing * 2., 0. } };
    for( size_t i = 0; i < 2; ++ i ) {
        solver.add_geometry( BEMGeometry::create_plane( 
            -260., 0., 260., ground_height, ground_rail_offsets[i], 40, 30 ) );
    }

    // Create rf rails and store their identifier
    Real rf_rail_offsets[][3] = {
        { 0., -gap_height / 2 - dc_height - rf_height - spacing, 0. },
        { 0., gap_height / 2 + dc_height + spacing, 0. } };
    for( size_t i = 0; i < 2; ++ i ) {
        rf_geoms.push_back(
            solver.add_geometry( BEMGeometry::create_plane( 
                -260., 0., 260., rf_height, rf_rail_offsets[i], 80, 30 ) ) );
    }

    // Create dc electrodes inside rf rails and store their identifiers
    Real dc_offsets[][3] = {
        {0., -gap_height / 2 - dc_height, dc_depth},
        {0., gap_height / 2, dc_depth}};
    for( int x = -4; x < 4; ++x )
    for( size_t y = 0; y < 2; ++ y ) {
        Real* offsets = dc_offsets[y];
        offsets[0] = dc_width * x + dc_spacing * x;
        dc_geoms.push_back(
            solver.add_geometry( BEMGeometry::create_plane( 
                0., 0., dc_width, dc_height, offsets, 10, 10 ) ) );
    }

    /*
    Real inner_ground_offsets[][3] = {
        {0., -inner_ground_offset - inner_ground_height, inner_ground_depth},
        {0., inner_ground_offset, inner_ground_depth} };
    for( size_t i = 0; i < 2; ++i ) {
        solver.add_geometry( create_plane( -300., 0., 300., 
            inner_ground_height, inner_ground_offsets[i], 10, 10 ) );
    }
    */
}

int main( int argc, char** argv ) {
    PetscInitialize( &argc, &argv, 0, 0 );
    BEMSolver solver( argc, argv );

    // Create chip trap.  Dimensions are:
    // x - axial, along the trap
    // y - the other direction along the trap, perpendicular to rails
    // z - vertical, out of the plane of the trap
    std::vector<size_t> rf_geoms, dc_geoms;
    //create_chip_trap( solver, rf_geoms, dc_geoms );
	load_trap( argv[1], solver, rf_geoms, dc_geoms );

    // Dimensions of the 3 dimensional space in the center of the trap
    // that the potential will be calculated over (in microns)
    // Potential is calculated with micron resolution in x and z,
    // but 2 micron resolution in y
    const int dx = 400, dy = 30, dz = 50;
    //const Real offsets[3] = { -dx/2., -dy, 40. };
    const Real offsets[3] = { 1235., -dy + 1176, 40. };

    const size_t ntest = dx*dy*dz;
    Real* test_vertices = new Real[ntest*3];
    Real* test_results = new Real[ntest];

    Real* vertex = test_vertices;
    for( size_t x = 0; x < dx; ++x )
    for( size_t z = 0; z < dz; ++z ) 
    for( size_t y = 0; y < dy; ++y ) {
        *vertex++ = offsets[0] + x;
        *vertex++ = offsets[1] + 2*y;
        *vertex++ = offsets[2] + z;
    }

    // The ordering of the extents and deltas is switched because the 
    // coordinate system that the program to analyze these potentials
    // uses is different than the one used here
    Vec vextents, vdeltas, voltages;
    Real extents[3] = { dy, dz, dx };
    Real deltas[3] = { 2, 1, 1 };

    VecCreateSeq( MPI_COMM_WORLD, 3, &vextents );
    VecPlaceArray( vextents, extents );
    PetscObjectSetName( (PetscObject)vextents, "Extents" );

    VecCreateSeq( MPI_COMM_WORLD, 3, &vdeltas );
    VecPlaceArray( vdeltas, deltas );
    PetscObjectSetName( (PetscObject)vdeltas, "Deltas" );

    // Create a h5 output file
    PetscViewer viewer;
    PetscViewerHDF5Open( PETSC_COMM_WORLD, "output.h5", FILE_MODE_WRITE,
        &viewer );

    // Add the extents and resolution of the potential to the "Attributes"
    // group with the names "Extents" and "Deltas" respectively
    PetscViewerHDF5PushGroup( viewer, "/Attributes" );
    VecView( vextents, viewer );
    VecView( vdeltas, viewer );
    
    for( size_t i = 0; i < dc_geoms.size()+1; ++i ) {
        std::cout << "Solving for " << i << std::endl;

        std::stringstream ss;
        ss << i;
        std::string potname = ss.str();

		if( false ) {
			if( i == 0 ) {
				// First iteration solves for the potential with all of
				// the rf electrodes charged.  All of the electrodes
				// should have been set to ground when they were created.
				for( size_t j = 0; j < rf_geoms.size(); ++j )
					solver.geometry[ rf_geoms[j] ]->voltage = 1.0;
			} else {
				// Each dc electrode is then charged independently and its 
				// potential calculated with everything else grounded
				solver.geometry[ dc_geoms[i-1] ]->voltage = 1.0;
			}

			// Resolve the BEM problem with the new voltages and then
			// extract the results at our sampling points
			solver.solve();
			// Resulting surface charges can be saved to use for visualization
			// and debugging purposes
			solver.save_results( "thedatters" + potname + ".txt", 
				"thetris.txt" );

			// Reset the voltage of whatever we just solved for to be zero 
			// This way we keep all but one electrode set to zero volts and
			// solve for the effect of each electrode separately.
			if( i == 0 ) {
				for( size_t j = 0; j < rf_geoms.size(); ++j )
					solver.geometry[ rf_geoms[j] ]->voltage = 0.0;
			} else {
				solver.geometry[ dc_geoms[i-1] ]->voltage = 0.0;
			}
		} else {
			solver.load_results( "thedatters" + potname + ".txt",
				"thetris.txt" );
		}

		// Calculate voltages at test points
        solver.voltages( ntest, test_vertices, test_results );

        // Store the potential under "Attributes/potentialDueToSurface"
        // with name set by electrode number
        // The rf electrodes will be number 0, with the dc electrodes
        // starting at 1 and proceeding sequentially
        VecCreateSeq( MPI_COMM_WORLD, ntest, &voltages );
        VecPlaceArray( voltages, test_results );
        PetscObjectSetName( (PetscObject)voltages, potname.c_str() );
        
        PetscViewerHDF5PushGroup( viewer, 
            "/Attributes/potentialDueToSurface" );
        VecView( voltages, viewer );

        VecDestroy( &voltages );
        solver.clear();
    }

    PetscViewerDestroy( &viewer );
    VecDestroy( &vextents );
    VecDestroy( &vdeltas );
    VecDestroy( &voltages );

    delete [] test_vertices;
    delete [] test_results;

    PetscFinalize();
};

    
