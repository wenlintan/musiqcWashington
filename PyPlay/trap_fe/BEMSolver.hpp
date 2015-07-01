
#include <petscksp.h>
#include <vector>

#include "BEMGeometry.hpp"

#pragma once

class BEMSolver {
public:
    BEMSolver( int argc, char** argv );
    ~BEMSolver();

    size_t add_geometry( BEMGeometry* geometry );

    void solve();
    void clear();

    void save_results( const std::string& vert_file,
        const std::string& index_file );
    void load_results( const std::string& vert_file,
        const std::string& index_file );

    void charges( size_t geo, Real* results );
    void voltages( size_t nverts, Real* vertices, Real* results );

    std::vector< BEMGeometry* > geometry;
private:
    void triangle_data( Real* vertices, size_t* triangle, size_t npts,
        Real* u, Real* v, Real* phi, Real* normal, Real* JxW );

    void update_system();
	void allocate();

    size_t nvertices;
    Mat A;
    Vec x, b;
    KSP ksp;    
};

