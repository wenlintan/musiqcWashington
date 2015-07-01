#ifndef RENDER_TARGET__H
#define RENDER_TARGET__H

#include "stdafx.h"
#include "resource.h"

class RenderTarget: public State 
{
public:
	enum Targets { BACK=100, FRONT };

	RenderTarget( ushort w, ushort h, bool z_buf = true ): 
			State( Resource::RENDER_TARGET ), Width( w ), Height( h ), ZBuffering( z_buf )
	{}

	//must be called before loading into renderer
	virtual void attach( const shared_ptr<DataTexture>& dt )	{ Attachments.push_back( dt ); }
	
	virtual void reset_targets()								{ Targets.resize(0); }
	virtual void add_target( uint tar )							{ Targets.push_back( tar ); }

	vector< const shared_ptr<DataTexture> >	Attachments;
	vector< uint >							Targets;

	ushort		Width, Height;
	bool		ZBuffering;
};

#endif