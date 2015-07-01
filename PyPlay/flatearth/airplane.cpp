
#include "airplane.h"

Airplane Airplane::simple_model() {

	//from Airplane J( pg 543 - 549 )
	Airplane p;

	//float S, c, b;									// wing area, chord length, wing span
	p.S = 150.f;	p.c = 5.0f;	p.b = 30.0f;			// ft^2, ft, ft

	//float mass, W;									// weight
	p.mass = 6000.0f / 32.f;	p.W = 6000.0f;			// slugs, lbs

	//float x_cg;										// CG from leading edge of wing
	p.x_cg = 0.25f*p.c;									// ft

	//Matrix33 I;										// intertial matrix 
	p.I = Matrix33( 7985.f,			0.0f,		0.0f,
					0.0f,			3326.f,		0.0f,
					0.0f,			0.0f,		11183.f );	// slug*ft^2


	//float C_L_0, C_L_a, C_L_a_dot, C_L_q;			// lift coefficients
	p.C_L_0 = 0.19f;		p.C_L_a = 4.81f;		p.C_L_a_dot = 1.8f;		p.C_L_q = 3.7f;

	//float C_D_0, C_D_a;							// drag coefficients
	p.C_D_0 = 0.0200;		p.C_D_a = 0.130f;

	//float C_m_0, C_m_a, C_m_a_dot, C_m_q;			// moments
	p.C_m_0 = 0.025;		p.C_m_a = -0.668f;		p.C_m_a_dot = -6.64f;	p.C_m_q = -14.3f;

	//float C_n_b, C_n_r, C_l_p;					// yaw moment coefficient due to side slip angle
	p.C_n_b = 0.1052f;		p.C_n_r = -0.1433f;		p.C_l_p = -0.440f;

	//float C_T;									// thrust coefficients
	p.C_T = 0.0f;		//TODO: Real value?

	//float C_m_de, C_l_da, C_n_dr;					// control
	p.C_m_de = -1.07f;		p.C_l_da = 0.1788f;		p.C_n_dr = -0.0365f;

	return p;
}


AirplaneState::InternalState AirplaneState::internal_state( const ControlSurfaceSet& control, float break_hp, const Vector3f& wind ) {

	float rho = 0.00237691267925741f*pow( 1-6.87558563248308e-06f*position.z, 4.25591641274834f);
	float q_bar = 0.5f * rho * velocity.length_sq();				// dynamic pressure

	Matrix33 to_plane = Matrix33::build_rotation_matrix( angles );
	Vector3f wind_plane = to_plane*wind;

	Vector3f air = velocity - wind_plane;
	float alpha = atan2( air.z, air.x );
	float beta = atan2( air.y, air.x );

	float C_L = plane.C_L_0 + plane.C_L_a*alpha + plane.C_L_q*rotation.y;
	float C_D = plane.C_D_0 + plane.C_D_a*alpha;

	Vector3f force( -C_D*plane.S*q_bar + break_hp * 550 / velocity.x, 
					0.0f, 
					-C_L*plane.S*q_bar );

	Matrix33 from_plane = Matrix33::build_rotation_matrix( -angles );
	Vector3f world_force = from_plane*force;

	world_force += Vector3f( 0.0f, 0.0f, plane.W );
	force = to_plane * world_force;

	float C_m = plane.C_m_0 + plane.C_m_a*alpha + plane.C_m_q*rotation.y + plane.C_m_de*control.elevator;
	float C_l = plane.C_l_p*rotation.x + plane.C_l_da*control.aileron;
	float C_n = plane.C_n_b*beta + plane.C_n_r*rotation.z + plane.C_n_dr*control.rudder;

	float Ma = C_m*plane.S*q_bar*plane.b;
	float La = C_l*plane.S*q_bar*plane.b;
	float Na = C_n*plane.S*q_bar*plane.b;

	/*
	Pdot=(c1*R+c2*P)*Q      +c3*(La+Lt)+c4*(Na+Nt);
	Qdot=c5*P*R-c6*(P*P-R*R)+c7*(Ma+Mt);
	Rdot=(c8*P-c2*R)*Q      +c4*(La+Lt)+c9*(Na+Nt);
	*/

	Vector3f rotation_dot( 
		(plane.I.m00*rotation.z + plane.I.m01*rotation.x)*rotation.y + plane.I.m02*La + plane.I.m10*Na,
		plane.I.m11*rotation.x*rotation.z - plane.I.m12*(rotation.x*rotation.x - rotation.z*rotation.z) + plane.I.m20*Ma,
		(plane.I.m21*rotation.x - plane.I.m02*rotation.z)*rotation.y + plane.I.m10*La + plane.I.m22*Na );

	InternalState s;
	s.alpha = alpha;			s.beta = beta;
	s.force = force;			s.rotation_dot = rotation_dot;
	return s;
}


void AirplaneState::update( const ControlSurfaceSet& control, float break_hp, const Vector3f& wind, float dt ) {
	
	state = internal_state( control, break_hp, wind );

	position += velocity * dt;
	velocity += state.force * dt;

	angles += rotation * dt;
	rotation += state.rotation_dot * dt;
}

void AirplaneRenderer::render( const shared_ptr<Renderer>& rend ) {
	rend->vertex_source_proje( vertices );

	DrawCallInfo info( Renderer::TRI, -1, state.position, state.angles, Color( Vector3ub(255, 0, 0) ), true );
	rend->draw_vertices_proje( info );
}

void AirplaneRenderer::setup_follow_camera( const shared_ptr<Camera>& cam ) {
	if( state.velocity.length_sq() >= G_EPSILON ) {
		cam->set(	state.position - ( state.velocity + Vector3f( 0.2f, 0.0f, 0.2f ) ).normalize()*4.0f, 
					state.position - ( state.velocity + Vector3f( 0.2f, 0.0f, 0.2f ) ).normalize()*3.0f, 
					Vector3f( 0.0f, 0.0f, 1.0f ) ); 
	} else {
		cam->set(	state.position - Vector3f(0.2f, -1.0f, 0.2f ).normalize()*4.0f, 
					state.position - Vector3f(0.2f, -1.0f, 0.2f ).normalize()*3.0f, Vector3f( 0.0f, 0.0f, 1.0f ) ); 
	}

}

void AirplaneRenderer::create_simple_model() {
	Vector3f b1( 0.0f, -1.0f, 0.0f  ), b2( -.666f, 0.666f, 0.0f  ), b3( .666f, 0.666f, 0.0f );
	Vector3f t1( 0.0f, 0.0f, 0.0f ),  t2( 0.0f, 0.666f, 0.0f ),   t3( 0.0f, 0.666f, 0.4f );

	vertices.push_back( b1 );	vertices.push_back( b2 );	vertices.push_back( b3 );
	vertices.push_back( t1 );	vertices.push_back( t3 );	vertices.push_back( t2 );
}
