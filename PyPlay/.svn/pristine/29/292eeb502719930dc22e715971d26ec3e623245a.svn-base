
#ifndef AIRPLANE__H
#define AIRPLANE__H

#include "graphics_core/stdafx.h"

#include "graphics_core/math.h"
#include "graphics_core/renderer.h"
#include "graphics_core/camera.h"

class ControlSurfaceSet {
public:
	float elevator, aileron, rudder;
};

class Airplane {
public:

	float S, c, b;									// wing area, chord length, wing span
	float mass, W;									// weight

	float x_cg;										// CG from leading edge of wing
	Matrix33 I;										// intertial matrix

	float C_L_0, C_L_a, C_L_a_dot, C_L_q;			// lift coefficients
	float C_D_0, C_D_a;								// drag coefficients

	float C_m_0, C_m_a, C_m_a_dot, C_m_q;			// moments
	float C_n_b, C_n_r, C_l_p;						// yaw moment coefficient due to side slip angle

	float C_T;										// thrust coefficients
	float C_m_de, C_l_da, C_n_dr;					// control

	static Airplane simple_model();
	static Airplane read( const string& filename );
};

class AirplaneState {
public:

	const Airplane& plane;
	AirplaneState( const Airplane& plane_ ):  plane( plane_ )
	{}

	Vector3f velocity;		// U, V, W (with respect to the plane)
	Vector3f rotation;

	Vector3f angles;		// phi, theta, psi
	Vector3f position;

	void update( const ControlSurfaceSet& control, float break_hp, const Vector3f& wind, float dt );

private:
	struct InternalState {
		float alpha, beta;

		Vector3f force, rotation_dot;
	};

	InternalState	state;
	InternalState internal_state( const ControlSurfaceSet& control, float break_hp, const Vector3f& wind );

};

class AirplaneRenderer {
public:

	const AirplaneState& state;
	AirplaneRenderer( const AirplaneState& state_ ): state( state_ )
	{
		create_simple_model();
	}

	void setup_follow_camera( const shared_ptr<Camera>& cam );
	void render( const shared_ptr<Renderer>& rend );

private:
	void create_simple_model();
	vector< Vector3f >	vertices;
};






#endif