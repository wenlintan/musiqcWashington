
#include <boost/asio.hpp>
#include <boost/thread.hpp>

#include <boost/function.hpp>
#include <boost/array.hpp>

#include "component.hpp"

void wrap_network();

struct NetworkView: Component {
	typedef boost::shared_ptr<NetworkView> pointer_type;

	typedef unsigned short entity_id_type;
	entity_id_type entity_id;

	typedef unsigned short network_id_type;
	network_id_type network_id;

	enum Serialization { ReliableDelta, UnreliableFullState };
	enum ComponentSource { AllComponents, FirstComponent };
	enum Routing { All, PotentiallyVisible, Others, Single };

	Serialization serialization;
	ComponentSource source;
	Routing routing;

	Component::Type component;

	NetworkView(): Component( Component::NetworkView ),
		serialization( UnreliableFullState ), 
		source( FirstComponent ), routing( All )
	{}
};

#if 0
class ClientData {
public:
	typedef State state_type;
	typedef State::entity_id_type entity_id_type;
	typedef State::network_id_type network_id_type;
	typedef boost::shared_ptr<state_type> state_ptr_type;

	ClientData( boost::asio::io_service& service ):
		socket( service ), reliable_socket( service ), connecting( true ) 
	{}

	bool			connecting;
	unsigned long 	address;
	unsigned short 	port;

	network_id_type network_id;
	state_ptr_type	input_state;

	void reliable_connect( const std::string& baseline, state_ptr_type s ); 
	void connect( boost::asio::ip::udp::endpoint ep );

	void add_rel_data( const std::string& data ) {
		reliable_data += data;
	}

	void add_data( const std::string& data ) {
		output_data += data;
	}

	void rel_send();
	void send();

private:
	typedef boost::system::error_code error_type;
	typedef boost::array< char, 1024 > buffer_type;

	void handle_rel_recv( const error_type& error, size_t bytes );
	void handle_rel_send( const error_type& error, size_t bytes );

	void handle_connecting_recv( std::string& s );

	void handle_recv( const error_type& error, size_t bytes );
	void handle_send( const error_type& error, size_t bytes );

	std::string		baseline_data;

	buffer_type		output_buffer;
	std::string		output_data;
	typedef boost::asio::ip::udp::socket socket_type;
	socket_type 	socket;

	buffer_type				reliable_buffer;
	std::string				reliable_input, reliable_data;

public: //temporary access for server, needs workaround
	typedef boost::asio::ip::tcp::socket reliable_socket_type;
	reliable_socket_type 	reliable_socket;
};

class Server {
public:
	typedef State state_type;
	typedef State::entity_id_type entity_id_type;
	typedef State::network_id_type network_id_type;

	typedef boost::shared_ptr<state_type> state_ptr_type;
	typedef boost::shared_ptr< ClientData > client_ptr_type;

	struct ClientInfo {
		ClientInfo( boost::asio::ip::tcp::endpoint& ep ):
			address( ep.address().to_v4().to_ulong() ),
			port( ep.port() )
		{}

		unsigned long 	address;
		unsigned short 	port;
		network_id_type network_id;
	};

	typedef state_ptr_type(connect_cb_sig)( ClientInfo );
	typedef boost::function< connect_cb_sig > connect_cb_type;

	typedef std::string(new_entity_cb_sig)( state_ptr_type );
	typedef boost::function< new_entity_cb_sig > new_entity_cb_type;

private:
	typedef boost::system::error_code error_type;
	typedef boost::array< char, 1024 > buffer_type;

	double				dt;
	buffer_type			recv_buffer;

	boost::asio::io_service 		service;
	boost::thread					thread;

	boost::asio::ip::udp::socket 	sock;
	boost::asio::ip::udp::endpoint	remote_endpt;
	boost::asio::ip::tcp::acceptor	acceptor;
	boost::asio::deadline_timer		timer;

	typedef entity_id_type output_key_type;
	typedef std::vector< client_ptr_type > client_data_type;
	typedef std::map< output_key_type, state_ptr_type > entity_state_type;

	client_data_type		client_data;
	entity_state_type		entity_states;

	connect_cb_type			connect_cb;
	new_entity_cb_type		new_entity_cb;

	void start_accept();
	void handle_accept( const error_type& error, size_t bytes );
	void handle_rel_accept( client_ptr_type c, const error_type& error );
	void handle_tick( const error_type& error );

	void do_update( state_ptr_type ent );
	void do_run();

public:
	Server( double dt, connect_cb_type conn, new_entity_cb_type new_ent );
	void update( state_ptr_type ent );
	
	template< typename T >
	void update_all( T begin, T end ) {
		while( begin != end ) {
			update( *begin );
			++begin;
		}
	}

	void run();
	void stop();
};

class Client {
public:
	typedef Server::entity_id_type entity_id_type;
	typedef Server::network_id_type network_id_type;

	typedef Server::state_type state_type;
	typedef Server::state_ptr_type state_ptr_type;

	typedef state_ptr_type(connect_cb_sig)( entity_id_type );
	typedef boost::function< connect_cb_sig > connect_cb_type;

	struct NewEntityData {
		NewEntityData( std::string d, state_ptr_type s ):
			data( d ), state( s )
		{}

		std::string data;
		state_ptr_type state;
	};

	typedef NewEntityData(new_entity_cb_sig)( std::string s );
	typedef boost::function< new_entity_cb_sig > new_entity_cb_type;

private:
	typedef boost::system::error_code error_type;
	typedef boost::array< char, 1024 > buffer_type;

	buffer_type			reliable_buffer;
	buffer_type			recv_buffer;

	bool				connecting;
	double				dt;

	boost::asio::io_service			service;
	boost::thread					thread;

	boost::asio::ip::udp::socket	sock;
	boost::asio::ip::udp::endpoint	server_endpt;
	boost::asio::ip::tcp::socket	reliable_sock;
	boost::asio::deadline_timer		timer;

	state_ptr_type					input_state;
	std::string						input_data;
	std::string						rel_data;

	typedef std::map< entity_id_type, state_ptr_type > entity_state_type;
	entity_state_type				entity_states;

	connect_cb_type					connect_cb;
	new_entity_cb_type				new_entity_cb;

	void handle_connect( const error_type& error );
	void handle_rel_recv( const error_type& error, size_t bytes );
	void handle_rel_send( const error_type& error, size_t bytes );

	void handle_recv( const error_type& error, size_t bytes );
	void handle_send( const error_type& error, size_t bytes );
	void handle_tick( const error_type& error );

	void do_send( const std::string& data );
	void do_rel_send( const std::string& data );

	std::string& do_rel_updates( std::string& s );
	void do_input( state_ptr_type ent );
	void do_run();

public:
	Client( double dt, new_entity_cb_type new_ent );
	void connect( const std::string& host, const std::string& port,
		const std::string& rel_port, connect_cb_type callback );

	void input( state_ptr_type input );
	void run();
	void stop();
};
#endif

