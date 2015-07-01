
#include "rocket_system.hpp"

#include <sdl.h>
#include <gl/gl.h>

#include <Rocket/Core.h>
#include <Rocket/Controls.h>
#include <Rocket/Debugger.h>

#include <boost/python.hpp>
using namespace boost::python;

struct rocket_string_to_python {
	static PyObject* convert( Rocket::Core::String const& s ) {
		return boost::python::incref(
			boost::python::object( s.CString() ).ptr() );
	}
};

struct rocket_string_from_python {
	rocket_string_from_python() {
		converter::registry::push_back(
			&convertible,
			&construct,
			type_id< Rocket::Core::String >() );
	}

	static void* convertible( PyObject* obj_ptr ) {
		if( !PyBytes_Check( obj_ptr ) )	return 0;
		return obj_ptr;
	}

	static void construct( PyObject* obj_ptr,
		converter::rvalue_from_python_stage1_data* data ) {

		void* storage = (
			(converter::rvalue_from_python_storage<
				Rocket::Core::String >*)data)->storage.bytes;

		new (storage) Rocket::Core::String(
			PyBytes_AsString( obj_ptr ) );
		data->convertible = storage;
	}
};

class PyEventListener: public Rocket::Core::EventListener {
public:
	virtual void process_event( Rocket::Core::Event& event ) = 0;
	virtual void ProcessEvent( Rocket::Core::Event& event ) {
		process_event( event );
	}
};

class PyEventListenerWrapper: public PyEventListener,
   public wrapper<PyEventListener> {
public:
	virtual void process_event( Rocket::Core::Event& event ) {
		this->get_override("process_event")( boost::ref(event) );
	}

};

void wrap_rocket() {
	to_python_converter< Rocket::Core::String, rocket_string_to_python>();
	rocket_string_from_python();

	class_< Rocket::Core::Element, boost::noncopyable >
		( "RocketElement", no_init ) 
		//TODO: This wrapping of add_event_handler does not correctly
		//take ownership of the passed EventListener
		.def( "add_event_listener", &Rocket::Core::Element::AddEventListener )
		.def( "get_element_by_id", &Rocket::Core::Element::GetElementById,
		   return_internal_reference<>() )

		.def( "has_attribute", 
			&Rocket::Core::Element::HasAttribute )
		.def( "get_string_attribute",
			&Rocket::Core::Element::GetAttribute<Rocket::Core::String> )
		.def( "get_int_attribute",
			&Rocket::Core::Element::GetAttribute<int> )
		.def( "set_string_attribute",
			&Rocket::Core::Element::SetAttribute<Rocket::Core::String> )
		.def( "set_int_attribute",
			&Rocket::Core::Element::SetAttribute<int> )
		
		.def( "get_property",
			&Rocket::Core::Element::GetProperty<Rocket::Core::String> )
		.def( "set_property",
			(bool (Rocket::Core::Element::*)( const Rocket::Core::String&,
				const Rocket::Core::String& ) )
			&Rocket::Core::Element::SetProperty )
		;

	class_< Rocket::Core::Event, boost::noncopyable >( "RocketEvent" )
		.def( "get_current_element", &Rocket::Core::Event::GetCurrentElement,
			return_internal_reference<>() )
		.def( "get_type", &Rocket::Core::Event::GetType,
			return_value_policy<copy_const_reference>() )
		.def( "get_string_parameter", 
			&Rocket::Core::Event::GetParameter<Rocket::Core::String> )
		.def( "get_int_parameter",
			&Rocket::Core::Event::GetParameter<int> )
		;

	class_< Rocket::Core::EventListener, boost::noncopyable >
		( "InternalRocketEventListener", no_init )
		;

	class_< PyEventListenerWrapper, PyEventListenerWrapper*, 
		bases<Rocket::Core::EventListener>, boost::noncopyable >
		( "RocketEventListener" )
		.def( "process_event", pure_virtual(&PyEventListener::process_event) )
		;

	class_< RocketDocument, RocketDocument::pointer_type,
		bases<Component>, boost::noncopyable >( "RocketDocument",
			init< const std::string& >() )
		.def( "get_element_by_id", &RocketDocument::get_element_by_id,
		   return_internal_reference<>() )
		.def( "contains_point", &RocketDocument::contains_point )
		.def_readwrite( "filename", &RocketDocument::filename )
		;

	class_< RocketSystem, RocketSystem::pointer_type, bases<System>, 
		boost::noncopyable >( "RocketSystem" )
		.def( "load_font", &RocketSystem::load_font )
		.def( "get_root_element", &RocketSystem::get_root_element,
			return_internal_reference<>() )
		.def( "end", &RocketSystem::end )

		.def( "handle_keyboard", &RocketSystem::handle_keyboard )
		.def( "handle_mouse_move", &RocketSystem::handle_mouse_move )
		.def( "handle_mouse_click", &RocketSystem::handle_mouse_click )
		;
}

class RocketSystemInterface: public Rocket::Core::SystemInterface {
public:
	float GetElapsedTime() { return SDL_GetTicks() / 1000.f; }

};

class RocketRendererInterface: public Rocket::Core::RenderInterface, 
	public BaseRendererSystem {
public:
	void RenderGeometry( Rocket::Core::Vertex* vertices, int num_vertices,
		int* indices, int num_indices, Rocket::Core::TextureHandle texture,
		const Rocket::Core::Vector2f& translation) {
	
		glDisable( GL_DEPTH_TEST );
		glEnable( GL_BLEND );
		glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

		glMatrixMode( GL_PROJECTION );
		glLoadIdentity();
		glOrtho( 0, 800, 600, 0, -1, 1 );

		glMatrixMode( GL_MODELVIEW );
		glLoadIdentity();
		glTranslatef( translation.x, translation.y, 0 );

		glVertexPointer( 2, GL_FLOAT, sizeof(Rocket::Core::Vertex), 
			&vertices[0].position );
		glColorPointer( 4, GL_UNSIGNED_BYTE, sizeof(Rocket::Core::Vertex),
			&vertices[0].colour );

		if( texture ) {
			glTexCoordPointer( 2, GL_FLOAT, sizeof(Rocket::Core::Vertex),
				&vertices[0].tex_coord );
			glEnableClientState( GL_TEXTURE_COORD_ARRAY );

			glEnable( GL_TEXTURE_2D );
			Texture tex( 0, *((TextureData::pointer_type*)texture) );
			bind_texture( tex );
		}

		glEnableClientState( GL_VERTEX_ARRAY );
		glEnableClientState( GL_COLOR_ARRAY );
		glDrawElements( GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, indices );
		glDisableClientState( GL_VERTEX_ARRAY );
		glDisableClientState( GL_COLOR_ARRAY );

		if( texture ) {
			glDisableClientState( GL_TEXTURE_COORD_ARRAY );
			glDisable( GL_TEXTURE_2D );
		}

		glEnable( GL_DEPTH_TEST );
		glDisable( GL_BLEND );
	}

	void EnableScissorRegion( bool enable ) {
		if( enable )	glEnable( GL_SCISSOR_TEST );
		else			glDisable( GL_SCISSOR_TEST );
	}

	void SetScissorRegion( int x, int y, int width, int height ) {
		glScissor(x, 600 - y - height, width, height );
	}

	bool LoadTexture( Rocket::Core::TextureHandle& tex, 
		Rocket::Core::Vector2i& dim, const Rocket::Core::String& src ) {

		TextureData::pointer_type tdata( new TextureData( src.CString() ) );
		load_texture( *tdata );

		dim.x = tdata->w;
		dim.y = tdata->h;
		tex = (Rocket::Core::TextureHandle)(
			new TextureData::pointer_type( tdata ) );
		return true;
	}

	bool GenerateTexture( Rocket::Core::TextureHandle& tex,
		const Rocket::Core::byte* data, const Rocket::Core::Vector2i& dim ) {

		TextureData::pointer_type tdata( new TextureData( 
			dim.x, dim.y, 4, 2, TextureData::Byte, 
			const_cast<unsigned char*>(data) ) );
		load_texture( *tdata );

		tex = (Rocket::Core::TextureHandle)(
			new TextureData::pointer_type( tdata ) );
		return true;
	}

	void ReleaseTexture( Rocket::Core::TextureHandle& texture ) {
		TextureData::pointer_type* td = (TextureData::pointer_type*)texture;
		delete td;
	}
};

class TileChooserWidget;
class TileChooserElement: public Rocket::Core::Element {
	friend class TileChooserWidget;
public:
	TileChooserElement(	const Rocket::Core::String& tag );
	~TileChooserElement();

	void OnRender();
	void OnLayout();

protected:
	TileChooserWidget* widget;
};

class TileChooserWidget: public Rocket::Core::EventListener {
public:
	TileChooserWidget( TileChooserElement* parent_ ):
		texture_dirty( true ), texture_dim(0, 0), 
		parent( parent_ ), x( 0 ), y( 0 )
	{
		parent->SetClientArea( Rocket::Core::Box::CONTENT );

		parent->SetProperty( "overflow-x", "hidden" );
		parent->SetProperty( "overflow-y", "hidden" );

		Rocket::Core::XMLAttributes attributes;
		attributes.Set( "id", "chosen-tile" );
		selected = Rocket::Core::Factory::InstanceElement( 
			parent, "*", "div", attributes );

		parent->AppendChild( selected, false );
		selected->RemoveReference();

		Rocket::Core::XMLAttributes tileattrs;
		tileattrs.Set( "src", "background.bmp" );
		tileset = Rocket::Core::Factory::InstanceElement(
			parent, "img", "img", tileattrs );

		parent->AppendChild( tileset, false );
		tileset->RemoveReference();
		tileset->AddEventListener( "click", this, true );
	}

	~TileChooserWidget() {
		parent->RemoveEventListener( "click", this, true );
		parent->RemoveChild( selected );
		parent->RemoveChild( tileset );
	}

	void on_render() { 
		std::string tiles( parent->GetAttribute<Rocket::Core::String>(
			"tileset", "" ).CString() );

		if( tiles != loaded_tiles ) {
			texture_dirty = true;
			loaded_tiles = tiles;
			tileset->SetAttribute( "src", tiles.c_str() );
			tileset->GetIntrinsicDimensions( texture_dim );
			on_layout();
		}
	}

	void on_layout() {
		Rocket::Core::Box box = parent->GetBox();
		float width = box.GetSize( Rocket::Core::Box::PADDING ).x;
		Rocket::Core::ElementScroll* scroll = parent->GetElementScroll();

		if( texture_dim.x > parent->GetClientWidth() ) {
			scroll->EnableScrollbar( 
				Rocket::Core::ElementScroll::HORIZONTAL, width );
		} else {
			scroll->DisableScrollbar(
				Rocket::Core::ElementScroll::HORIZONTAL );
		}

		if( texture_dim.y > parent->GetClientHeight() ) {
			scroll->EnableScrollbar(
				Rocket::Core::ElementScroll::VERTICAL, width );
		} else {
			scroll->DisableScrollbar(
				Rocket::Core::ElementScroll::VERTICAL );
		}

		parent->SetContentBox( Rocket::Core::Vector2f(0., 0.), texture_dim );
		scroll->FormatScrollbars();

		if( texture_dirty ) {
			Rocket::Core::Vector2f pos = 
				box.GetPosition(Rocket::Core::Box::CONTENT);
			tileset->SetOffset( pos, parent );
			texture_dirty = false;
		}

		Rocket::Core::Box tilebox;
		tilebox.SetContent( texture_dim );
		tilebox.SetEdge( Rocket::Core::Box::BORDER, Rocket::Core::Box::TOP, 1);
		tileset->SetBox( tilebox );

		int twidth = parent->GetAttribute<int>( "tile_width", 32 );
		int theight = parent->GetAttribute<int>( "tile_height", 32 );

		Rocket::Core::Box selbox;
		selbox.SetContent( Rocket::Core::Vector2f( twidth, theight ) );
		for( size_t i = 0; i < Rocket::Core::Box::NUM_EDGES; ++i )
			selbox.SetEdge( Rocket::Core::Box::BORDER, 
				(Rocket::Core::Box::Edge)i, 1);
		selected->SetBox( selbox );

		selected->SetOffset( 
			Rocket::Core::Vector2f( x*twidth, y*theight ) -
			selected->GetBox().GetPosition(), parent );


		//Rocket::Core::ElementUtilities::PositionElement(
		//	selected, Rocket::Core::Vector2f( x*twidth, y*theight ),
		//	Rocket::Core::ElementUtilities::TOP_LEFT );
	}

	void set_selected_tile_x( int x_ ) 	{ x = x_; }
	void set_selected_tile_y( int y_ ) 	{ y = y_; }

protected:
	void ProcessEvent( Rocket::Core::Event& event ) {
		if( event.GetType() == "click" ) {
			int mouse_x = event.GetParameter<int>( "mouse_x", 0 );
			int mouse_y = event.GetParameter<int>( "mouse_y", 0 );

			int twidth = parent->GetAttribute<int>( "tile_width", 32 );
			int theight = parent->GetAttribute<int>( "tile_height", 32 );

			Rocket::Core::Vector2f off = 
				Rocket::Core::Vector2f( mouse_x, mouse_y ) - 
				tileset->GetAbsoluteOffset();

			x = off.x / twidth;
			y = off.y / theight;
			parent->SetAttribute( "tile_x", x );
			parent->SetAttribute( "tile_y", y );
			parent->DirtyLayout();
		}
	}

	bool texture_dirty;
	std::string loaded_tiles;
	Rocket::Core::Vector2f texture_dim;

	TileChooserElement* parent;
	Rocket::Core::Element* selected, *tileset;
	int x, y;
};

TileChooserElement::TileChooserElement(	const Rocket::Core::String& tag ): 
	Rocket::Core::Element( tag ) 
{
	widget = new TileChooserWidget( this );
}

TileChooserElement::~TileChooserElement() {
	delete widget;
}

void TileChooserElement::OnRender() {
	widget->on_render();
}

void TileChooserElement::OnLayout() {
	widget->on_layout();
}

struct RocketDocumentInternals {
	Rocket::Core::ElementDocument* document;
};

struct RocketSystemInternals {
	RocketSystemInternals():
		rocket_focused( true ), context( 0 )
	{}

	bool rocket_focused;
	Rocket::Core::Context* context;
};

RocketDocument::RocketDocument( const std::string& fname ):
	Component( Component::GUIWindow ), filename( fname )
{
	if( !RocketSystem::context )
		throw "libRocket must be initialized before loading windows.";

	internals = new RocketDocumentInternals();
	internals->document = RocketSystem::context->context->LoadDocument(
		filename.c_str() );

	// Set tagged element to contain window title
	Rocket::Core::Element* title = internals->document->
		GetElementById( "title" );
	if( title )		title->SetInnerRML( internals->document->GetTitle() );

	internals->document->Focus();
	internals->document->Show();
}

Rocket::Core::Element* RocketDocument::get_element_by_id( 
	const std::string& id ) {
	return internals->document->GetElementById( id.c_str() );
}

bool RocketDocument::contains_point( const Vector2f& pt ) {
	return internals->document->
		IsPointWithinElement( Rocket::Core::Vector2f( pt.d[0], pt.d[1] ) );
}

RocketSystemInternals* RocketSystem::context = 0;
RocketSystem::RocketSystem(): internals( new RocketSystemInternals() ) {
	context = internals;

	Rocket::Core::SetSystemInterface( new RocketSystemInterface() );
	Rocket::Core::SetRenderInterface( new RocketRendererInterface() );
	Rocket::Core::Initialise();

	internals->context = Rocket::Core::CreateContext( "main",
		Rocket::Core::Vector2i( 800, 600 ) );

	Rocket::Controls::Initialise();
	Rocket::Debugger::Initialise( internals->context );
	Rocket::Debugger::SetVisible( true );

	Rocket::Core::ElementInstancer* custom = 
		new Rocket::Core::ElementInstancerGeneric< TileChooserElement >();
	Rocket::Core::Factory::RegisterElementInstancer( "tilechooser", custom );
	custom->RemoveReference();
}

RocketSystem::~RocketSystem() {
	internals->context->RemoveReference();
	Rocket::Core::Shutdown();
	delete internals;
}

void RocketSystem::load_font( const std::string& name ) {
	Rocket::Core::FontDatabase::LoadFontFace( name.c_str() );
}

Rocket::Core::Element* RocketSystem::get_root_element() {
	return internals->context->GetRootElement();
}

void RocketSystem::update( Entity::pointer_type ent ) {
	if( !ent->has_component( Component::GUIWindow ) )
		return;

	RocketDocument& doc =
		static_cast< RocketDocument& >(
			ent->get_component( Component::GUIWindow ) );
}


void RocketSystem::end() {
	internals->context->Update();
	internals->context->Render();
}

Rocket::Core::Input::KeyIdentifier remap_key( int code ) {
	switch( code ) {
		case SDL_SCANCODE_BACKSPACE:return Rocket::Core::Input::KI_BACK;
		case SDL_SCANCODE_TAB:		return Rocket::Core::Input::KI_TAB;
		case SDL_SCANCODE_CLEAR:	return Rocket::Core::Input::KI_CLEAR;
		case SDL_SCANCODE_RETURN:	return Rocket::Core::Input::KI_RETURN;
		case SDL_SCANCODE_PAUSE:	return Rocket::Core::Input::KI_PAUSE;
		case SDL_SCANCODE_ESCAPE:	return Rocket::Core::Input::KI_ESCAPE;
		case SDL_SCANCODE_SPACE:	return Rocket::Core::Input::KI_SPACE;
		case SDL_SCANCODE_APOSTROPHE:	return Rocket::Core::Input::KI_OEM_7;
		case SDL_SCANCODE_EQUALS:	return Rocket::Core::Input::KI_OEM_PLUS;
		case SDL_SCANCODE_COMMA:	return Rocket::Core::Input::KI_OEM_COMMA;
		case SDL_SCANCODE_MINUS:	return Rocket::Core::Input::KI_OEM_MINUS;
		case SDL_SCANCODE_PERIOD:	return Rocket::Core::Input::KI_OEM_PERIOD;
		case SDL_SCANCODE_SLASH:	return Rocket::Core::Input::KI_OEM_2;
		case SDL_SCANCODE_SEMICOLON:return Rocket::Core::Input::KI_OEM_1;
		case SDL_SCANCODE_LEFTBRACKET:	return Rocket::Core::Input::KI_OEM_4;
		case SDL_SCANCODE_BACKSLASH:	return Rocket::Core::Input::KI_OEM_5;
		case SDL_SCANCODE_RIGHTBRACKET:	return Rocket::Core::Input::KI_OEM_6;
		case SDL_SCANCODE_GRAVE:		return Rocket::Core::Input::KI_OEM_3;

		case SDL_SCANCODE_0:		return Rocket::Core::Input::KI_0;
		case SDL_SCANCODE_1:		return Rocket::Core::Input::KI_1;
		case SDL_SCANCODE_2:		return Rocket::Core::Input::KI_2;
		case SDL_SCANCODE_3:		return Rocket::Core::Input::KI_3;
		case SDL_SCANCODE_4:		return Rocket::Core::Input::KI_4;
		case SDL_SCANCODE_5:		return Rocket::Core::Input::KI_5;
		case SDL_SCANCODE_6:		return Rocket::Core::Input::KI_6;
		case SDL_SCANCODE_7:		return Rocket::Core::Input::KI_7;
		case SDL_SCANCODE_8:		return Rocket::Core::Input::KI_8;
		case SDL_SCANCODE_9:		return Rocket::Core::Input::KI_9;

		case SDL_SCANCODE_A:		return Rocket::Core::Input::KI_A;
		case SDL_SCANCODE_B:		return Rocket::Core::Input::KI_B;
		case SDL_SCANCODE_C:		return Rocket::Core::Input::KI_C;
		case SDL_SCANCODE_D:		return Rocket::Core::Input::KI_D;
		case SDL_SCANCODE_E:		return Rocket::Core::Input::KI_E;
		case SDL_SCANCODE_F:		return Rocket::Core::Input::KI_F;
		case SDL_SCANCODE_G:		return Rocket::Core::Input::KI_G;
		case SDL_SCANCODE_H:		return Rocket::Core::Input::KI_H;
		case SDL_SCANCODE_I:		return Rocket::Core::Input::KI_I;
		case SDL_SCANCODE_J:		return Rocket::Core::Input::KI_J;
		case SDL_SCANCODE_K:		return Rocket::Core::Input::KI_K;
		case SDL_SCANCODE_L:		return Rocket::Core::Input::KI_L;
		case SDL_SCANCODE_M:		return Rocket::Core::Input::KI_M;
		case SDL_SCANCODE_N:		return Rocket::Core::Input::KI_N;
		case SDL_SCANCODE_O:		return Rocket::Core::Input::KI_O;
		case SDL_SCANCODE_P:		return Rocket::Core::Input::KI_P;
		case SDL_SCANCODE_Q:		return Rocket::Core::Input::KI_Q;
		case SDL_SCANCODE_R:		return Rocket::Core::Input::KI_R;
		case SDL_SCANCODE_S:		return Rocket::Core::Input::KI_S;
		case SDL_SCANCODE_T:		return Rocket::Core::Input::KI_T;
		case SDL_SCANCODE_U:		return Rocket::Core::Input::KI_U;
		case SDL_SCANCODE_V:		return Rocket::Core::Input::KI_V;
		case SDL_SCANCODE_W:		return Rocket::Core::Input::KI_W;
		case SDL_SCANCODE_X:		return Rocket::Core::Input::KI_X;
		case SDL_SCANCODE_Y:		return Rocket::Core::Input::KI_Y;
		case SDL_SCANCODE_Z:		return Rocket::Core::Input::KI_Z;
						

		default:			return Rocket::Core::Input::KI_UNKNOWN;
	}
}

Rocket::Core::Input::KeyModifier remap_key_modifier( int mod ) {
	int res = 0;
	if( mod & KMOD_SHIFT )		res |= (int)Rocket::Core::Input::KM_SHIFT;
	if( mod & KMOD_CTRL )		res |= (int)Rocket::Core::Input::KM_CTRL;
	if( mod & KMOD_ALT )		res |= (int)Rocket::Core::Input::KM_ALT;
	if( mod & KMOD_GUI )		res |= (int)Rocket::Core::Input::KM_META;
	if( mod & KMOD_NUM )		res |= (int)Rocket::Core::Input::KM_NUMLOCK;
	if( mod & KMOD_CAPS )		res |= (int)Rocket::Core::Input::KM_CAPSLOCK;
	return (Rocket::Core::Input::KeyModifier)res;
}

int remap_mouse_button( int sdl_button ) {
	return sdl_button - 1;
}

char ascii_map[4][51] =
{
    // shift off and capslock off
    {
		0, ' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b',
		'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
		'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ';', '=', ',', '-',
		'.', '/', '`', '[', '\\', ']', '\'', 0, 0
	},

	// shift on and capslock off
    {
		0, ' ', ')', '!', '@', '#', '$', '%', '^', '&', '*', '(', 'A', 'B',
		'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
		'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ':', '+', '<', '_',
		'>', '?', '~', '{', '|', '}', '"', 0, 0
	},

	// shift on and capslock on
    {
		0, ' ', ')', '!', '@', '#', '$', '%', '^', '&', '*', '(', 'a', 'b',
		'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
		'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ':', '+', '<', '_',
		'>', '?', '~', '{', '|', '}', '"', 0, 0
	},

	// shift off and capslock on
    {
		0, ' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B',
		'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
		'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ';', '=', ',', '-',
		'.', '/', '`', '[', '\\', ']', '\'', 0, 0
	}      
};

char keypad_map[2][18] = 
{
	{
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\n', '*', '+',
		0, '-', '.', '/', '='
	},

	{
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '\n', '*', '+', 0, '-', 0, '/', '='
	}
};

Rocket::Core::word remap_text_input(
	Rocket::Core::Input::KeyIdentifier key, 
	Rocket::Core::Input::KeyModifier mod ) {

	if( key <= Rocket::Core::Input::KI_OEM_102 ) {
		bool shift = mod & Rocket::Core::Input::KM_SHIFT;
		bool caps = mod & Rocket::Core::Input::KM_CAPSLOCK;

		if( shift && !caps )	return ascii_map[1][ key ];
		if( shift && caps )		return ascii_map[2][ key ];
		if( !shift && caps )	return ascii_map[3][ key ];
		return ascii_map[0][ key ];
	} else if( key <= Rocket::Core::Input::KI_OEM_NEC_EQUAL ) {
		bool num = mod & Rocket::Core::Input::KM_NUMLOCK;
		int nkey = key - Rocket::Core::Input::KI_NUMPAD0;
		
		if( num )		return keypad_map[0][ nkey ];
		return keypad_map[1][ nkey ];
	}

	return 0;
}

bool RocketSystem::handle_keyboard( int code, bool down ) {
	if( !internals->rocket_focused )
		return false;

	Rocket::Core::Input::KeyIdentifier rocket_key = remap_key( code );
	Rocket::Core::Input::KeyModifier rocket_mod = 
		remap_key_modifier( SDL_GetModState() );

	if( down ) {
		if( remap_text_input( rocket_key, rocket_mod ) != 0 ) {
			Rocket::Core::word w = remap_text_input( rocket_key, rocket_mod );
			internals->context->ProcessTextInput( w	);
		}

		internals->context->ProcessKeyDown( rocket_key, rocket_mod );
		return true;
	} else {
		internals->context->ProcessKeyUp( rocket_key, rocket_mod );
		return true;
	}
}

bool RocketSystem::handle_mouse_move( int x, int y, int dx, int dy ) {
	Rocket::Core::Input::KeyModifier mod =
		remap_key_modifier( SDL_GetModState() );
	internals->context->ProcessMouseMove( x, y, mod );
	return false;
}

bool RocketSystem::handle_mouse_click( int button, int x, int y, bool down ) {
	int rocket_button = remap_mouse_button( button );
	Rocket::Core::Input::KeyModifier mod =
		remap_key_modifier( SDL_GetModState() );

	int i = 0;
	for( ; i < internals->context->GetNumDocuments(); ++i ) {
		Rocket::Core::Element* doc = internals->context->GetDocument( i );
		if( doc->IsPointWithinElement( Rocket::Core::Vector2f( x, y ) ) &&
		 	doc->GetProperty( "visibility" )->ToString() != "hidden" )
			break;
	}

	if( i == internals->context->GetNumDocuments() ) {
		internals->context->GetFocusElement()->Blur();
		internals->rocket_focused = false;
		return false;
	}

	internals->rocket_focused = true;

	if( down )
		internals->context->ProcessMouseButtonDown( rocket_button, mod );
	else
		internals->context->ProcessMouseButtonUp( rocket_button, mod );
	return true;
}

