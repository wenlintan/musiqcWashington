
#include <fstream>
#include <sstream>

#include "BEMSolver.hpp"

BEMSolver::BEMSolver( int argc, char** argv ): nvertices( 0 ),
	A( 0 ), b( 0 ), x( 0 ) {
}

BEMSolver::~BEMSolver() {
    MatDestroy( &A );
    VecDestroy( &b );
    VecDestroy( &x );
}

size_t BEMSolver::add_geometry( BEMGeometry* geom ) {
    geometry.push_back( geom );
    return geometry.size()-1;
}

void BEMSolver::allocate() {
    size_t new_nvertices = 0;
    for( size_t g = 0; g < geometry.size(); ++g ) {
        geometry[g]->offset = new_nvertices;
        new_nvertices += geometry[g]->nvertices;
    }

	if( new_nvertices != nvertices ) {
		nvertices = new_nvertices;
		MatCreateMPIDense( PETSC_COMM_WORLD, PETSC_DECIDE, PETSC_DECIDE,
			nvertices, nvertices, 0, &A );
		VecCreateMPI( PETSC_COMM_WORLD, PETSC_DECIDE, nvertices, &x );
		VecDuplicate( x, &b );
	}
}

void BEMSolver::solve() {
	allocate();

    MatZeroEntries( A );
    VecZeroEntries( x );
	VecZeroEntries( b );
    
    //PetscLogStage stage;
    //PetscLogStageRegister( "Assembly", &stage );
    //PetscLogStagePush( stage );
    update_system();

    MatAssemblyBegin( A, MAT_FINAL_ASSEMBLY );
    MatAssemblyEnd( A, MAT_FINAL_ASSEMBLY );
    VecAssemblyBegin( x );
    VecAssemblyEnd( x );
    //PetscLogStagePop();

    KSPCreate( PETSC_COMM_WORLD, &ksp );
    KSPSetOperators( ksp, A, A, DIFFERENT_NONZERO_PATTERN );
    KSPSetFromOptions( ksp );
    KSPSolve( ksp, x, b );  
    KSPDestroy( &ksp );

    //Vec tmp;
    //VecDuplicate( x, &tmp );
    //MatMult( A, b, tmp );
    
    //VecView( tmp, PETSC_VIEWER_STDOUT_WORLD );
    //VecView( b, PETSC_VIEWER_STDOUT_WORLD );
}

void BEMSolver::clear() {
}

void BEMSolver::save_results( const std::string& vert_file,
    const std::string& tri_file ) {

    std::ofstream file( vert_file.c_str() );
    std::ofstream trifile( tri_file.c_str() );

    for( size_t g = 0; g < geometry.size(); ++g ) {
        BEMGeometry& geo = *geometry[g];
        Real* geocharges = new Real[ geo.nvertices ];
        charges( g, geocharges );

        for( size_t i = 0; i < geo.nvertices; ++i ) {
            file << geo.vertices[i*3] << " " << geo.vertices[i*3+1] << " " << 
                geo.vertices[i*3+2] << " " << geocharges[i] << std::endl;
        }

        for( size_t i = 0; i < geo.nindices/3; ++i ) {
            trifile << geo.offset + geo.indices[i*3] << " " << 
                geo.offset + geo.indices[i*3+1] << " " <<
                geo.offset + geo.indices[i*3+2] << std::endl;
        }

        delete [] geocharges;
    }

    file.close();
    trifile.close();
}

void BEMSolver::load_results( const std::string& vert_file,
    const std::string& tri_file ) {

	allocate();

    PetscInt low, high;
    VecGetOwnershipRange( b, &low, &high );

	size_t index = 0;
	std::ifstream file( vert_file.c_str() );
	PetscReal x, y, z, c;
	while( file >> x >> y >> z >> c ) {
		if( index < (size_t)low || index >= (size_t)high ) continue;
		VecSetValue( b, index, c, INSERT_VALUES );
		++index;
	}
}

void BEMSolver::charges( size_t geo, Real* results ) {
    Vec local_b;
    VecScatter ctx;
    VecScatterCreateToZero( b, &ctx, &local_b );
    VecScatterBegin( ctx, b, local_b, INSERT_VALUES, SCATTER_FORWARD );
    VecScatterEnd( ctx, b, local_b, INSERT_VALUES, SCATTER_FORWARD );
    VecScatterDestroy( &ctx );

    PetscScalar* charges;
    VecGetArray( local_b, &charges );

    for( size_t v = 0; v < geometry[geo]->nvertices; ++v ) {
        results[v] = charges[v + geometry[geo]->offset];
    }

    VecRestoreArray( local_b, &charges );
    VecDestroy( &local_b );
}

void BEMSolver::voltages( size_t nverts, Real* vertices, Real* results ) {
    const Real oofpen = 1 / 4. / 3.141592654; // 9e9;

    Vec local_b;
    VecScatter ctx;
    VecScatterCreateToZero( b, &ctx, &local_b );
    VecScatterBegin( ctx, b, local_b, INSERT_VALUES, SCATTER_FORWARD );
    VecScatterEnd( ctx, b, local_b, INSERT_VALUES, SCATTER_FORWARD );
    VecScatterDestroy( &ctx );
    
    PetscScalar* charges;
    VecGetArray( local_b, &charges );

    //const size_t ngauss = 4;
    //Real gauss_w[] = { 2*0.15902, 2*0.090979, 2*0.15902, 2*0.090979 };
    //Real gauss_u[] = { 0.15505, 0.644949, 0.15505, 0.644949 };
    //Real gauss_v[] = { 0.17856, 0.075031, 0.66639, 0.280020 };

    const size_t ngauss = 12;
    Real gauss_w[] = { 
        0.05084490637, 0.05084490637, 0.05084490637,
        0.11678627573, 0.11678627573, 0.11678627573,
        0.08285107562, 0.08285107562, 0.08285107562,
        0.08285107562, 0.08285107562, 0.08285107562 };
    Real gauss_u[] = {
        0.87382197102, 0.06308901449, 0.06308901449,
        0.50142650966, 0.24928674517, 0.24928674517,
        0.63650249912, 0.63650249912, 0.31035245103, 
        0.31035245103, 0.05314504984, 0.05314504984 };
    Real gauss_v[] = {
        0.06308901449, 0.87382197102, 0.06308901449,
        0.24928674517, 0.50142650966, 0.24928674517,
        0.31035245103, 0.05314504984, 0.05314504984,
        0.63650249912, 0.63650249912, 0.31035245103 }; 

    Real *pts = new Real[3*ngauss], JxW;
    for( size_t v = 0; v < nverts; ++v )
        results[v] = 0.0;

    for( size_t g = 0; g < geometry.size(); ++g ) {
        BEMGeometry& geo = *geometry[g];
        for( size_t v = 0; v < nverts; ++v) {
            for( size_t j = 0; j < geo.nindices; j += 3 ) {
                triangle_data( geo.vertices, &geo.indices[j],
                    ngauss, gauss_u, gauss_v, pts, 0, &JxW );

                for( size_t g = 0; g < ngauss; ++g ) {
                    Real dx = vertices[v*3] - pts[g*3],
                        dy = vertices[v*3+1] - pts[g*3+1],
                        dz = vertices[v*3+2] - pts[g*3+2];
                    
                    Real scale = oofpen * JxW * gauss_w[g] / 
                        sqrt( dx*dx + dy*dy + dz*dz );

                    Real div[] = { 1., 1., 1. };
                    if( geo.hard_edges ) for( size_t dv = 0; dv < 3; ++dv ) {
                        Real* edge = &geo.hard_edges[
                            geo.indices[j+dv]*4 ];
                        if( edge[0] < 4 ) continue;

                        size_t idx = geo.indices[j+dv];
                        Real dxj = pts[g*3] - geo.vertices[idx*3],
                            dyj = pts[g*3+1] - geo.vertices[idx*3+1],
                            dzj = pts[g*3+2] - geo.vertices[idx*3+2];

                        Real dp = dxj*edge[1] + dyj*edge[2] + dzj*edge[3];
                        dxj -= dp * edge[1];
                        dyj -= dp * edge[2];
                        dzj -= dp * edge[3];

                        Real dist = sqrt( dxj*dxj + dyj*dyj + dzj*dzj );
                        div[dv] *= pow( dist, 3.141592654 / edge[0] -1 );
                    }

                    results[v] += scale * (1 - gauss_u[g] - gauss_v[g])*div[0]*
                        charges[ geo.offset + geo.indices[j] ];
                    results[v] += scale * ( gauss_u[g] ) * div[1] *
                        charges[ geo.offset + geo.indices[j+1] ];
                    results[v] += scale * ( gauss_v[g] ) * div[2] *
                        charges[ geo.offset + geo.indices[j+2] ];
                }
            }
        }
    }

    delete [] pts;
    VecRestoreArray( local_b, &charges );
    VecDestroy( &local_b );
}

void BEMSolver::triangle_data( Real* vertices, size_t* triangle, size_t npts,
    Real* u, Real* v, Real* pts, Real* normal, Real* JxW ) {

    Real *p1 = &vertices[ triangle[0]*3 ],
        *p2 = &vertices[ triangle[1]*3 ],
        *p3 = &vertices[ triangle[2]*3 ];

    Real dxdu = p2[0] - p1[0], dydu = p2[1] - p1[1], dzdu = p2[2] - p1[2];
    Real dxdv = p3[0] - p1[0], dydv = p3[1] - p1[1], dzdv = p3[2] - p1[2];

    for( size_t i = 0; i < npts; ++i ) {
        pts[i*3 + 0] = p1[0] + dxdu*u[i] + dxdv*v[i];
        pts[i*3 + 1] = p1[1] + dydu*u[i] + dydv*v[i];
        pts[i*3 + 2] = p1[2] + dzdu*u[i] + dzdv*v[i];
    }

    Real Jx = dydu * dzdv - dzdu * dydv,
        Jy = -dxdu * dzdv + dzdu * dxdv,
        Jz =  dxdu * dydv - dydu * dxdv;
    *JxW = sqrt( Jx*Jx + Jy*Jy + Jz*Jz ) / 2.;

    if( normal ) {
        normal[0] = Jx / *JxW;
        normal[1] = Jy / *JxW;
        normal[2] = Jz / *JxW;
    }
}

void BEMSolver::update_system() {
    const Real oofpen = 1. / 4. / 3.141592654; //9e9;

    PetscInt low, high;
    VecGetOwnershipRange( x, &low, &high );

    //const size_t ngauss = 4;
    //Real gauss_w[] = { 2*0.15902, 2*0.090979, 2*0.15902, 2*0.090979 };
    //Real gauss_u[] = { 0.15505, 0.644949, 0.15505, 0.644949 };
    //Real gauss_v[] = { 0.17856, 0.075031, 0.66639, 0.280020 };

    const size_t ngauss = 12;
    Real gauss_w[] = { 
        0.05084490637, 0.05084490637, 0.05084490637,
        0.11678627573, 0.11678627573, 0.11678627573,
        0.08285107562, 0.08285107562, 0.08285107562,
        0.08285107562, 0.08285107562, 0.08285107562 };
    Real gauss_u[] = {
        0.87382197102, 0.06308901449, 0.06308901449,
        0.50142650966, 0.24928674517, 0.24928674517,
        0.63650249912, 0.63650249912, 0.31035245103, 
        0.31035245103, 0.05314504984, 0.05314504984 };
    Real gauss_v[] = {
        0.06308901449, 0.87382197102, 0.06308901449,
        0.24928674517, 0.50142650966, 0.24928674517,
        0.31035245103, 0.05314504984, 0.05314504984,
        0.63650249912, 0.63650249912, 0.31035245103 }; 

    Real *ptsj = new Real[3*ngauss], JxWj;

    for( size_t gi = 0; gi < geometry.size(); ++gi )
    for( size_t gj = 0; gj < geometry.size(); ++gj ) {
        BEMGeometry& geoi = *geometry[gi];
        BEMGeometry& geoj = *geometry[gj];
        for( size_t i = 0; i < geoi.nvertices; ++i ) {
            size_t index = geoi.offset + i;
            if( index < (size_t)low || index >= (size_t)high ) continue;
            VecSetValue( x, index, geoi.voltage, INSERT_VALUES );

            for( size_t j = 0; j < geoj.nindices; j += 3 ) {
                triangle_data( geoj.vertices, &geoj.indices[j],
                    ngauss, gauss_u, gauss_v, ptsj, 0, &JxWj );

                for( size_t g = 0; g < ngauss; ++g ) {
                    Real dx = geoi.vertices[i*3] - ptsj[g*3],
                        dy = geoi.vertices[i*3+1] - ptsj[g*3+1],
                        dz = geoi.vertices[i*3+2] - ptsj[g*3+2];
                    
                    Real scale = oofpen * JxWj * gauss_w[g] / 
                        sqrt( dx*dx + dy*dy + dz*dz );

                    Real div[] = { 1., 1., 1. };
                    if( geoj.hard_edges ) for( size_t v = 0; v < 3; ++v ) {
                        Real* edge = &geoj.hard_edges[
                            geoj.indices[j+v]*4 ];
                        if( edge[0] < 4 ) continue;

                        size_t idx = geoj.indices[j+v];
                        Real dxj = ptsj[g*3] - geoj.vertices[idx*3],
                            dyj = ptsj[g*3+1] - geoj.vertices[idx*3+1],
                            dzj = ptsj[g*3+2] - geoj.vertices[idx*3+2];

                        Real dp = dxj*edge[1] + dyj*edge[2] + dzj*edge[3];
                        dxj -= dp * edge[1];
                        dyj -= dp * edge[2];
                        dzj -= dp * edge[3];

                        Real dist = sqrt( dxj*dxj + dyj*dyj + dzj*dzj );
                        div[v] *= pow( dist, 3.141592654 / edge[0] -1 );
                    }
                    
                    MatSetValue( A, index, geoj.offset + geoj.indices[j], 
                        scale * ( 1 - gauss_u[g] - gauss_v[g] ) * div[0],
                        ADD_VALUES );
                    MatSetValue( A, index, geoj.offset + geoj.indices[j+1],
                        scale * gauss_u[g] * div[1],
                        ADD_VALUES );
                    MatSetValue( A, index, geoj.offset + geoj.indices[j+2],
                        scale * gauss_v[g] * div[2],
                        ADD_VALUES );
                }
            }
        }
    }

    delete [] ptsj;
}
