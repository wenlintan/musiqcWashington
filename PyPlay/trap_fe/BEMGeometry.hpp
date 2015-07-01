
#include <iostream>

#include <petscksp.h>

#pragma once

// Use PETSC default real type
typedef PetscReal Real;

struct BEMGeometry {
	BEMGeometry() : nvertices( 0 ), nindices( 0 ), offset( 0 ),
		vertices( 0 ), hard_edges( 0 ), indices( 0 ), voltage( 0. )
	{}

    // Construct geometry holding a copy of data in arguments
    BEMGeometry( size_t nverts, Real* vert, 
        size_t nind, size_t* inds, Real* edges, Real volt ): 
        nvertices( nverts ), nindices( nind ), offset(0),
        vertices( new Real[nverts*3] ), hard_edges(0),
        indices( new size_t[nind] ), voltage( volt )
    {
        // Copy data into newly allocated arrays
        for( size_t i = 0; i < nverts*3; ++ i )
            vertices[i] = vert[i];
        for( size_t i = 0; i < nind; ++i )
            indices[i] = inds[i];

        if( edges ) {
            hard_edges = new Real[ 4*nverts ];
            for( size_t i = 0; i < 4*nverts; ++ i )
                hard_edges[i] = edges[i];
        }
    }

    // Allocate space for geometry without filling it
    BEMGeometry( size_t nverts, size_t nind, bool edges = false,
        Real volt = 0. ): nvertices( nverts ), nindices( nind ), offset(0),
        vertices( new Real[nverts*3] ), hard_edges(0),
        indices( new size_t[nind] ), voltage( volt )
    {
        if( edges )
            hard_edges = new Real[ 4*nverts ];
    }

    ~BEMGeometry() {
        delete [] vertices;
        delete [] hard_edges;
        delete [] indices;
    }

    static BEMGeometry* create_disc( size_t radius_prec, size_t theta_prec );
    static BEMGeometry* create_plane( 
        Real xmin, Real ymin, Real xmax, Real ymax,
        Real* offset, size_t x_prec, size_t y_prec );
    static BEMGeometry* create_cyl( 
        Real inner_radius, Real outer_radius, 
        Real z_min, Real z_max, Real* offset, 
        size_t z_prec, size_t r_prec, size_t theta_prec );

    size_t nvertices, nindices, offset;
    Real* vertices, *hard_edges;
    size_t* indices;
    Real voltage;

private:
    BEMGeometry( const BEMGeometry& other ) {}
};

std::istream& operator >>( std::istream& input, BEMGeometry& geom );


