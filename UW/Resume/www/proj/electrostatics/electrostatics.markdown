
### Electrostatics for Ion Traps

As described in my [summary of ion traps and what they're good for](/trap/) it's impossible to form a stable trap for a charged particle in three dimensions with electrostatics.  However by applying radio frequency voltage to one of the elctrodes a trap can be formed, and the dynamics of that trap can be analyzed assuming that one knows the magnitude of the time varying electric field created by the rf.  Luckily this is easy to find from the electrostatic voltage produced by the electrode that the rf is applied to, and therefore the entire trapping dynamics can be found from the dc electrostatic potentials of the trap.

### Finite Element Method

The finite element method relies on discretizing two dimensional surfaces that describe the boundaries of the geometry you want to simulate.  Then either Dirichlet or Neumann boundary conditions are imposed on the surfaces and the differential equation one is interested in is imposed between all pairs of surface elements.  Obviously for this technique to be useful there must a Green's function that can describe the effect of one point's charge (or whatever other physics variable is of interest) on all of space.  Luckily such a Green's function is very easy for two dimensional electrostatics.

%{\large\[V = \int_S \frac{1}{4\pi\epsilon_0}\frac{\sigma}{r}dA\]}%

This equation describes how to solve for the voltage anywhere in space induced by a surface charge $\sigma$ on some surface $S$.

I use PETSc to handle performing the necessary matrix inversion and deal with parallelize the matrix creation using MPI.  First, we assign indices to each piece of geometry in our master matrix and vector for the solution.  Since I'm currently not doing any dynamic geometry splitting or merging we can keep that very simple.

    #!c++
    void BEMSolver::solve() {
        nvertices = 0;
        for( size_t g = 0; g < geometry.size(); ++g ) {
            geometry[g]->offset = nvertices;
            nvertices += geometry[g]->nvertices;
        }

Solving a linear system such as $A \times x = b$ is very simple with PETSc, and can be found in several of their exmaples.

    #!c++
        MatCreateMPIDense( PETSC_COMM_WORLD, PETSC_DECIDE, PETSC_DECIDE,
            nvertices, nvertices, 0, &A );
        MatZeroEntries( A );

        VecCreateMPI( PETSC_COMM_WORLD, PETSC_DECIDE, nvertices, &x );
        VecZeroEntries( x );
        VecDuplicate( x, &b );
        
        update_system();

        MatAssemblyBegin( A, MAT_FINAL_ASSEMBLY );
        MatAssemblyEnd( A, MAT_FINAL_ASSEMBLY );
        VecAssemblyBegin( x );
        VecAssemblyEnd( x );

        KSPCreate( PETSC_COMM_WORLD, &ksp );
        KSPSetOperators( ksp, A, A, DIFFERENT_NONZERO_PATTERN );
        KSPSetFromOptions( ksp );
        KSPSolve( ksp, x, b );	
        KSPDestroy( &ksp );
    }


Finally we need to write the update\_system function, which will perform teh surface integrals defined above to create the matrix $A$ and the solution vector $b$. In order to accomplish this we must decide on how to approximate the surface integral, and how to approximate the surface charges across the surface.


The easiest method to approximate the surface charges is just to have free variables at each vertex and linearly interpolate between the three vertices that make up each triangle.  There are also higher order solutions to this problem, but you can accomplish roughly the same effect by increasing the resolution of the mesh used to approximate the surface. The integration is accomplished by finding Gaussian quadrature points that will give the approximation for the integral up to a certain order by sampling a relatively small number of points.  These can be solved for by finding the critical points for sample polynomials of the desired order.  In this case I use second order quadrature points.  To implement the update\_system function, I use a helper function that computes the sample points and the determinant of the Jacobian for a given triangle.

    #!c++
    void BEMSolver::triangle_data(Real* vertices, size_t* triangle, size_t npts,
        Real* u, Real* v, Real* pts, Real* normal, Real* JxW) {

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

Using that helper function we can easily create the necessary linear algebra constructs to solve for the surface charges on our mesh.

    #!cpp
    void BEMSolver::update_system() {
        const Real oofpen = 1. / 4. / 3.141592654;

        PetscInt low, high;
        VecGetOwnershipRange( x, &low, &high );

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

                        MatSetValue( A, index, geoj.offset + geoj.indices[j], 
                            scale * ( 1 - gauss_u[g] - gauss_v[g] ),
                            ADD_VALUES );
                        MatSetValue( A, index, geoj.offset + geoj.indices[j+1],
                            scale * gauss_u[g],
                            ADD_VALUES );
                        MatSetValue( A, index, geoj.offset + geoj.indices[j+2],
                            scale * gauss_v[g],
                            ADD_VALUES );
                    }
                }
            }
        }

        delete [] ptsj;
    }


### Results

The ion trap that I wanted to simulate is a surface electrode trap.  It has a pair of flat rf rails along either side and flat ground or dc electrodes running inbetween them.  The dc electrodes are segmented into many electrodes that can be easily controlled, allowing the operator to apply electric fields to move ions around the trapping region.  It is even possible to form multiple trapping regions and trap separate groups of ions in the same trap.  The trap works much the same way as the Paul Trap described [here](/trap/#paul_trap), except that all the electrodes are on a flat surface on a chip trap and the oscillating quadrupole is formed 40 to 100 microns above the trap surface.  The advantage of this design is that the trap can be reliably manufactured with etching and microfabrication techniques.

In order to quickly simulate the ion's response to different dc voltage solutions, the finite element simulation is asked to generate the surface charges for charging each electrode or rf rail separately to 1 Volt.  Since the problem is linear these solutions can then be scaled and added together to simulate the effect of applying any desired voltages to the electrodes.

<div class="gallery">
<a class="gallery-image statics" title="Charge distribution when rf rails are charged." href="images/rf_rails.png"><img class="gallery-thumbnail" src="images/rf_rails.jpg"/></a>
<a class="gallery-image statics" title="Charge distribution when one dc electrode is charged." href="images/dc_5.png"><img class="gallery-thumbnail" src="images/dc_5.jpg"/></a>
<a class="gallery-image statics" title="Charge distribution when one dc electrode is charged." href="images/dc_10.png"><img class="gallery-thumbnail" src="images/dc_10.jpg"/></a>
</div>

One the surface charges are solved for the voltages at any point in space can be calculated from the same integral Green's functions.  Currently I usually export a few dozen microns around the center of the trapping location.  In order to incorporate the effect of the rf, I approximate the electric field at each position by taking derivatives.  Ideally, this should be done using a separate FEM process, but this method is far easier.  The confining effect of the rf can be described by a pseudopotential

%\large\[\psi = \frac{q}{4 m \Omega^2} \lvert \vec{E} \rvert^2\]%

where q is the charge of the ion, m is its mass, $\Omega$ is the frequency of the rf applied to the rail, and $\vec{E}$ is the electric field.  The ion trapping dynamics behave exactly as though this pseuopotential were a real electric potential, and in fact it can just be added to the potentials from the other dc electrodes.

The potentials from each electrode separately are shown below.  The horizontal axis is along the length of the rf rails shown above, and the vertical axis is height above the surface of the trap.  The first image shows the strong radial confinement of the rf along the entire rail.  The dc electrode potentials have axial dependence, and combinations of them are used to provide axial confinement.

<div class="gallery">
<a class="gallery-image statics" title="Potential near trap center when rf rails are charged." href="images/yz_rf.png"><img class="gallery-thumbnail" src="images/yz_rf.jpg"/></a>
<a class="gallery-image statics" title="Potential near trap center when one dc electrode is charged." href="images/yz_5.png"><img class="gallery-thumbnail" src="images/yz_5.jpg"/></a>
<a class="gallery-image statics" title="Potential near trap center when one dc electrode is charged." href="images/yz_10.png"><img class="gallery-thumbnail" src="images/yz_10.jpg"/></a>
</div>

By applying appropriate voltages to each electrode we can finally generate an actual ion trap.  The ion trap is analyzed by using the GSL to fit a second order function to the potential at some starting point near the trap center.  The linear terms of the fits are used to move towards teh center of the trap and teh fitting is repeated.  The process continues until the linear terms are minimized, and the resulting second order terms are the trapping strengths.  Changing the dc voltages allows us to shuttle the bottom of the ion trap along the length of the trap.  We usually generate potentials centered every 5 microns along the trap and switch between them rapidly to move the ion around.  The results with actual ions seem to agree very well with the results expected from these calculations.

<div class="gallery">
<a class="gallery-image statics" title="Trapping potential positioned near left." href="images/yz_all_left.png"><img class="gallery-thumbnail" src="images/yz_all_left.jpg"/></a>
<a class="gallery-image statics" title="Trapping potential positioned near right." href="images/yz_all.png"><img class="gallery-thumbnail" src="images/yz_all.jpg"/></a>
</div>
