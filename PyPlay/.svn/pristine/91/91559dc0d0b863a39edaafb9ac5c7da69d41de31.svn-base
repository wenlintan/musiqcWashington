#ifndef LIGHT__H
#define LIGHT__H

#include "stdafx.h"
#include <gl/gl.h>

#include "resource.h"

struct LightColor {
	LightColor(): r(0.0), g(0.0), b(0.0), a(1.0)
	{}

	LightColor( float r_, float g_, float b_, float a_ = 1.0 ):
			r( r_ ), g( g_ ), b( b_ ), a( a_ )
	{}

	LightColor operator*( float scale ) {
		return LightColor( scale*r, scale*g, scale*b );
	}

	float r, g, b, a;
};

class Light: public State {
public:

	int				ID;
	int				Enabled, Point;

	LightColor		Ambient, Diffuse, Specular;
	Vector3f		PointPosition, DirectionalDirection;


	Light():  State(Resource::LIGHT), ID( 0 ), Enabled( false ), Point( true )
	{}

	void apply() {
		if( !Enabled ) {
			glDisable( GL_LIGHT0 + ID );
			return;
		}

		glEnable( GL_LIGHT0 + ID );
		glLightfv( GL_LIGHT0 + ID, GL_AMBIENT, &Ambient.r );
		glLightfv( GL_LIGHT0 + ID, GL_DIFFUSE, &Diffuse.r ); 
		glLightfv( GL_LIGHT0 + ID, GL_SPECULAR, &Specular.r ); 

		float data[4];
		if( Point )	{ data[0] = PointPosition.x; data[1] = PointPosition.y; 
					  data[2] = PointPosition.z; data[3] = 1.; }
		else		{ data[0] = DirectionalDirection.x; data[0] = DirectionalDirection.y; 
					  data[0] = DirectionalDirection.z; data[3] = 0.; }

		glLightfv( GL_LIGHT0 + ID, GL_POSITION, data );

	}
};

#endif


