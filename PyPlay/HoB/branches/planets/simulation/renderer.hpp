
#pragma once 
#include <map>

#include "system.hpp"
#include "renderer_components.hpp"

void wrap_renderer();

struct ScreenSystemInternals;
class ScreenSystem: public System {
	ScreenSystemInternals* internals;
	unsigned short	x, y;

public:
	typedef boost::shared_ptr<ScreenSystem> pointer_type;
	bool			use_multitexture, use_fbos, use_shaders;

	ScreenSystem( const unsigned short x, const unsigned short y );
	~ScreenSystem();

	void begin();
	void update( Entity::pointer_type ent );
	void end();

};

class BaseRendererSystem: public System {
public:
	static std::map< MeshVertexData::AttributeDataType, int > gl_type_map;

	void load_texture( TextureData& data );
	void bind_texture( Texture& texture );

	void create_rbo( Renderbuffer& rb );
	void create_fbo( Framebuffer& fb );
	void bind_fbo( Framebuffer& fb );

	// Shader bind functions
	void bind_program( Program& program, Mesh& mesh, Matrix4f& camera );
	void bind_variable( Program& program, Mesh& mesh,
		const std::string& name, ProgramVariable& variable );

	// Fixed function bind functions
	void ff_bind_camera( Matrix4f& trans );
	void ff_bind_vertex( MeshVertexData& data );
	void ff_bind_color( MeshVertexData& data );

};

class MeshRendererSystem: public BaseRendererSystem {

	void draw_mesh( Entity::pointer_type mesh, Mesh& m, Matrix4f& camera,
		RenderFlags camera_flags );

	std::vector< Entity::pointer_type > meshes;
	std::vector< std::pair<unsigned short, Entity::pointer_type> > cameras;

public:
	typedef boost::shared_ptr<MeshRendererSystem> pointer_type;

	void begin();
	void update( Entity::pointer_type ent );
	void end();
};

