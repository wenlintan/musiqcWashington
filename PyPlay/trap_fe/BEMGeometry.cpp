
#include "BEMGeometry.hpp"

std::istream& operator >>( std::istream& input, BEMGeometry& geom ) {
	delete [] geom.vertices;
	delete [] geom.indices;
	delete [] geom.hard_edges;

	std::string label;
	input >> label;

	input >> geom.nvertices;
	std::cout << geom.nvertices << " vertices" << std::endl;
	geom.vertices = new Real[ geom.nvertices*3 ];
	Real* vp = geom.vertices;
	for( size_t v = 0; v < geom.nvertices*3; ++v ) {
		input >> *vp++;
	}

	input >> label;
	input >> geom.nindices;
	geom.nindices *= 3;		// 3 indices per face
	geom.indices = new size_t[ geom.nindices ];
	std::cout << geom.nindices << " indices" << std::endl;
	size_t* ip = geom.indices;
	for( size_t i = 0; i < geom.nindices; ++i ) {
		input >> *ip++;
	}

	geom.hard_edges = 0;
	return input;	
}

BEMGeometry* BEMGeometry::create_disc( size_t radius_prec, size_t theta_prec ) {
    size_t r_res = radius_prec, t_res = theta_prec;
    size_t nverts = r_res*t_res + 1;
    size_t nindices = 3*2*t_res*(r_res-1) + 3*t_res;

    BEMGeometry* result = new BEMGeometry( nverts, nindices, true );
    Real* vert = result->vertices;
    Real* edge = result->hard_edges;
    size_t* index = result->indices;

    *vert++ = 0.; *vert++ = 0.; *vert++ = 0.;
    *edge++ = 3.141592654;
    edge += 3;

    for( size_t t = 0; t < t_res-1; ++t ) {
        *index++ = 0;   *index++ = t+1; *index++ = t+2;
    }
    *index++ = 0;   *index++ = t_res;   *index++ = 1;
        
    for( size_t r = 0; r < r_res; ++r ) for( size_t t = 0; t < t_res; ++t ) {
        Real radius = 1./r_res * (r+1);
        Real theta = 2*3.141592654/t_res * t;
        *vert++ = radius * cos( theta );
        *vert++ = radius * sin( theta );
        *vert++ = 0.;

        if( r == r_res-1 ) {
            *edge++ = 2*3.141592654;
            *edge++ = -sin( theta );
            *edge++ = cos( theta );
            *edge++ = 0.;
        } else {
            *edge++ = 3.141592654;
            edge += 3;
        }
    
        if( r > 0 && t > 0  ) {
            *index++ = 1 + t_res*(r-1) + (t-1);
            *index++ = 1 + t_res*r + (t-1);
            *index++ = 1 + t_res*r + t;

            *index++ = 1 + t_res*(r-1) + (t-1);
            *index++ = 1 + t_res*r + t;
            *index++ = 1 + t_res*(r-1) + t;
        } else if( r > 0 ) {
            *index++ = 1 + t_res*(r-1) + t_res-1;
            *index++ = 1 + t_res*r + t_res-1;
            *index++ = 1 + t_res*r + t;

            *index++ = 1 + t_res*(r-1) + t_res-1;
            *index++ = 1 + t_res*r + t;
            *index++ = 1 + t_res*(r-1) + t;
        }
    }

    return result;
}

BEMGeometry* BEMGeometry::create_plane( 
    Real xmin, Real ymin, Real xmax, Real ymax,
    Real* offset, size_t x_prec, size_t y_prec ) {

    if( x_prec < 2 ) x_prec = 2;
    if( y_prec < 2 ) y_prec = 2;
    size_t nverts = x_prec * y_prec;
    size_t nindices = 3*2*(x_prec-1)*(y_prec-1);

    BEMGeometry* result = new BEMGeometry( nverts, nindices, true );
    Real* vert = result->vertices;
    Real* edge = result->hard_edges;
    size_t* index = result->indices;

    for( size_t y = 0; y < y_prec; ++y )
    for( size_t x = 0; x < x_prec; ++x ) {
        *vert++ = xmin + (xmax - xmin) * x / (x_prec - 1) + offset[0];
        *vert++ = ymin + (ymax - ymin) * y / (y_prec - 1) + offset[1];
        *vert++ = offset[2];

        if( false && (x == 0 ||  y == 0 || x == x_prec-1 || y == y_prec-1 )) {
            *edge++ = 2*3.141592654;
            if( x == 0 || x == x_prec-1 ) {
                if( y == 0 ) {
                    *edge++ = 1. / sqrt(2.);
                    *edge++ = -1. / sqrt(2.);
                } else if( y == y_prec-1 ) {
                    *edge++ = 1. / sqrt(2.);
                    *edge++ = 1. / sqrt(2.);
                } else {
                    *edge++ = 0.;
                    *edge++ = 1.;
                }

                if( x == x_prec-1 )
                    *(edge-2) = -(*(edge-2));
            } else {
                *edge++ = 1.0;
                *edge++ = 0.0;
            }
            
            *edge++ = 0.0;
        } else {
            *edge++ = 3.141592654;
            edge += 3;
        }

        if( x > 0 && y > 0 ) {
            *index++ = (y-1) * x_prec + x-1;
            *index++ = (y-1) * x_prec + x;
            *index++ = (y) * x_prec + x;

            *index++ = (y-1) * x_prec + x-1;
            *index++ = (y) * x_prec + x;
            *index++ = (y) * x_prec + x-1;
        }

    }

    return result;
}


BEMGeometry* BEMGeometry::create_cyl( Real inner_radius, Real outer_radius, 
    Real z_min, Real z_max, Real* offset, 
    size_t z_prec, size_t r_prec, size_t theta_prec ) {
    
    if( r_prec < 3 )    r_prec = 3;
    size_t nverts = theta_prec * z_prec + 2*(r_prec-2) * theta_prec;
    nverts += (inner_radius > 0) ? theta_prec*z_prec: 2; 

    size_t nindices = 3*2*theta_prec*(z_prec-1) + 6*2*theta_prec*(r_prec-2);
    nindices += (inner_radius > 0) ? 
        3*2*theta_prec*(z_prec-1) + 6*2*theta_prec:
        3*2*theta_prec;

    BEMGeometry* result = new BEMGeometry( nverts, nindices, true );
    Real* vert = result->vertices;
    Real* edge = result->hard_edges;
    size_t* index = result->indices;

    for( size_t r = 0; r < 2; ++ r )
    for( size_t z = 0; z < z_prec; ++z )
    for( size_t t = 0; t < theta_prec; ++t ) {
        if( r == 1 && inner_radius == 0 ) continue;
        Real radius = r ? inner_radius : outer_radius;

        Real zval = z_min + (z_max - z_min)*z/(z_prec-1);
        Real theta = 2*3.141592654*t/theta_prec;

        *vert++ = radius * cos(theta) + offset[0];
        *vert++ = radius * sin(theta) + offset[1];
        *vert++ = zval + offset[2];

        if( z == 0 || z == z_prec-1 ) {
            *edge++ = 3*3.141592654 / 2;
            *edge++ = -sin( theta );
            *edge++ = cos( theta );
            *edge++ = 0;
        } else {
            *edge++ = 3.141592654;
            edge += 3;
        }

        if( z > 0 && t > 0 ) {
            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + t-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + t-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + t;

            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + t-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + t;
            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + t;
        } else if( z > 0 ) {
            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + theta_prec-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + theta_prec-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + t;

            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + theta_prec-1;
            *index++ = r*theta_prec*z_prec + theta_prec*z + t;
            *index++ = r*theta_prec*z_prec + theta_prec*(z-1) + t;
        }
    }

    size_t ioffset = 2 * theta_prec * z_prec;
    if( inner_radius == 0. ) {
        ioffset = theta_prec * z_prec + 2;
        *vert++ = offset[0];*vert++ = offset[1];*vert++ = z_min + offset[2];
        *edge++ = 3.141592654;
        edge += 3;

        *vert++ = offset[0];*vert++ = offset[1];*vert++ = z_max + offset[2];
        *edge++ = 3.141592654;
        edge += 3;

        for( size_t t = 0; t < theta_prec; ++t ) {
            *index++ = ioffset - 2;
            *index++ = ioffset + (t+1)%theta_prec;
            *index++ = ioffset + t;

            *index++ = ioffset - 1;
            *index++ = ioffset + (r_prec-2)*theta_prec + (t+1)%theta_prec;
            *index++ = ioffset + (r_prec-2)*theta_prec + t;
        }
    } else {
        for( size_t z = 0; z < 2; ++z )
        for( size_t t = 0; t < theta_prec; ++t ) {
            *index++ = theta_prec*z_prec + z*theta_prec*(z_prec-1) + t;
            *index++ = ioffset + z*(r_prec-2)*theta_prec + t;
            *index++ = ioffset + z*(r_prec-2)*theta_prec + (t+1)%theta_prec;

            *index++ = theta_prec*z_prec + z*theta_prec*(z_prec-1) + t;
            *index++ = ioffset + z*(r_prec-2)*theta_prec + (t+1)%theta_prec;
            *index++ = theta_prec*z_prec + z*theta_prec*(z_prec-1) + 
                (t+1)%theta_prec;
        }
    }

    for( size_t z = 0; z < 2; ++z ) 
    for( size_t r = 0; r < r_prec-2; ++r )
    for( size_t t = 0; t < theta_prec; ++t ) {
        Real zval = z ? z_max: z_min;
        Real theta = 2*3.141592654*t/theta_prec;
        Real radius = inner_radius + (outer_radius - inner_radius) *
            (r+1) / (r_prec-1);

        *vert++ = radius * cos( theta ) + offset[0];
        *vert++ = radius * sin( theta ) + offset[1];
        *vert++ = zval + offset[2];

        *edge++ = 3.141592654;
        edge += 3;

        if( r > 0 ) {
            *index++ = ioffset + z*theta_prec*(r_prec-2) + theta_prec*(r-1) + t;
            *index++ = ioffset + z*theta_prec*(r_prec-2) + theta_prec*r + t;
            *index++ = ioffset + z*theta_prec*(r_prec-2) + 
                theta_prec*r + (t+1)%theta_prec;

            *index++ = ioffset + z*theta_prec*(r_prec-2) + theta_prec*(r-1) + t;
            *index++ = ioffset + z*theta_prec*(r_prec-2) + 
                theta_prec*r + (t+1)%theta_prec;
            *index++ = ioffset + z*theta_prec*(r_prec-2) + 
                theta_prec*(r-1) + (t+1)%theta_prec;
        }
    }

    for( size_t z = 0; z < 2; ++z ) 
    for( size_t t = 0; t < theta_prec; ++t ) {
        *index++ = ioffset + z*theta_prec*(r_prec-2) + 
            theta_prec*(r_prec-3) + t;
        *index++ = z*theta_prec*(z_prec-1) + t;
        *index++ = z*theta_prec*(z_prec-1) + (t+1)%theta_prec;
        
        *index++ = ioffset + z*theta_prec*(r_prec-2) + 
            theta_prec*(r_prec-3) + t;
        *index++ = z*theta_prec*(z_prec-1) + (t+1)%theta_prec;
        *index++ = ioffset + z*theta_prec*(r_prec-2) + 
            theta_prec*(r_prec-3) + (t+1)%theta_prec;
    }

    return result;
}

