
#include <boost/python.hpp>
#include <boost/bind.hpp>

#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>

#include <boost/assign/list_of.hpp>

#include <boost/functional/value_factory.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/preprocessor/repetition/enum_params.hpp>

#include <iostream> // For debugging
#include <sstream>

#include "network.hpp"

using namespace boost::asio;
using namespace boost::asio::ip;

using namespace boost::python;

struct StateWrapper: State, wrapper<State> {
public:
	std::string serialize() {
		return call<std::string>( this->get_override( "serialize" ).ptr() );
	}

	std::string deserialize( const std::string& s ) {
		return call<std::string>( this->get_override( 
			"deserialize" ).ptr(), s );
	}
};

struct StateWrap: State {
	StateWrap( PyObject *p ): self(p)
	{}

	std::string serialize() {
		return call_method<std::string>( self, "serialize" );
	}

	std::string deserialize( const std::string& s ) {
		return call_method<std::string>( self, "deserialize", s );
	}

	PyObject* self;
};

template< typename T >
struct boost_function_arg_wrapper{
	typedef T result_type;
	T operator()( T t ) { return t; }
};
/*
template<>
struct boost_function_arg_wrapper< Server::state_ptr_type >{
	typedef pointer_wrapper< Server::state_ptr_type > result_type;
	result_type operator()( Server::state_ptr_type t ) {
		return ptr( t );
	}
};
*/

template< typename Signature >
struct boost_function_from_python {};

#define NARGS 1
template< typename R, BOOST_PP_ENUM_PARAMS( NARGS, typename T ) >
struct boost_function_from_python
	< R ( BOOST_PP_ENUM_PARAMS(NARGS, T) ) > 
{
	typedef boost::function< R ( BOOST_PP_ENUM_PARAMS(NARGS, T) ) > 
		wrapped_type;

	boost_function_from_python() {
		converter::registry::push_back(
			&convertible,
			&construct,
			type_id< wrapped_type >() );
	}

	static void* convertible( PyObject* obj_ptr ) {
		if( !PyCallable_Check( obj_ptr ) )	return 0;
		return obj_ptr;
	}

	static void construct( PyObject* obj_ptr,
		converter::rvalue_from_python_stage1_data* data ) {

		void* storage = (
			(converter::rvalue_from_python_storage<
				wrapped_type >*)data)->storage.bytes;

		R (&pycall)( PyObject*, 
			boost_function_arg_wrapper<T0>::result_type const &, 
			boost::type<R>* ) = call;

		// Must borrow an object here to hold onto a reference
		object obj( handle<>( borrowed( obj_ptr ) ) );
		new (storage) wrapped_type(
			boost::bind( pycall, 
				boost::bind( &object::ptr, obj ),
				boost::bind( boost_function_arg_wrapper<T0>(),
					boost::lambda::_1 ),
				(boost::type<R>*)0 )
			);

		data->convertible = storage;
	}
};

void wrap_network() {
	PyEval_InitThreads();

	boost_function_from_python< Server::connect_cb_sig >();
	boost_function_from_python< Server::new_entity_cb_sig >();

	boost_function_from_python< Client::connect_cb_sig >();
	boost_function_from_python< Client::new_entity_cb_sig >();

	enum_<State::Serialization>( "Serialization" )
		.value( "ReliableDelta", State::ReliableDelta )
		.value( "UnreliableFullState", State::UnreliableFullState )
		;

	enum_<State::Routing>( "Routing" )
		.value( "All", State::All )
		.value( "PotentiallyVisible", State::PotentiallyVisible )
		.value( "Others", State::Others )
		.value( "Single", State::Single )
		;

	class_<State, StateWrap, boost::shared_ptr<State>, boost::noncopyable >
			( "State" )
		.def_readwrite( "entity_id", &State::entity_id )
		.def_readwrite( "network_id", &State::network_id )
		.def_readwrite( "serialization", &State::serialization )
		.def_readwrite( "routing", &State::routing )

		.def( "serialize", pure_virtual(&StateWrap::serialize) )
		.def( "deserialize", pure_virtual(&StateWrap::deserialize) )
		;
	implicitly_convertible< StateWrapper*, State* >();

	class_< Server::ClientInfo, boost::noncopyable >
			( "ClientInfo", no_init )
		.def_readwrite( "address", &Server::ClientInfo::address )
		.def_readwrite( "port", &Server::ClientInfo::port )
		.def_readwrite( "network_id", &Server::ClientInfo::network_id )
		;

	class_< Server, boost::noncopyable  >( "Server", 
		init<double, Server::connect_cb_type, 
			Server::new_entity_cb_type>() )
		.def( "update", &Server::update )
		.def( "run", &Server::run )
		.def( "stop", &Server::stop )
		;

	class_< Client::NewEntityData >( "NewEntityData",
		init<std::string, Client::state_ptr_type>() )
		;

	class_< Client, boost::noncopyable  >( "Client", 
		init<double, Client::new_entity_cb_type>()	)
		.def( "connect", &Client::connect )
		.def( "input", &Client::input )
		.def( "run", &Client::run )
		.def( "stop", &Client::stop )
		;
}

struct AcquirePythonGIL {
	PyGILState_STATE gstate;
	AcquirePythonGIL() { gstate = PyGILState_Ensure(); }
	~AcquirePythonGIL() { PyGILState_Release(gstate); }
};

template< typename Derived >
struct ArchiveState: public State {
	std::string serialize() {
		std::ostringstream stream;
		boost::archive::binary_oarchive archive( stream );
		archive << (Derived&)(*this);
		return stream.str();
	}

	std::string deserialize( const std::string& data ) {
		std::istringstream stream( data );
		boost::archive::binary_iarchive archive( stream );
		archive >> (Derived&)(*this);

		std::string remainder( stream.str().substr( stream.tellg() ) );
		return remainder;
	}

};

struct Header: public ArchiveState<Header> {
	unsigned short length;
	Header( unsigned short length_ = 0 ): 
		length( length_ )
	{}

	using ArchiveState<Header>::serialize;
	using ArchiveState<Header>::deserialize;

	template< class Archive >
	void serialize( Archive& ar, const unsigned int version ) {
		ar & length;
	}
};

struct Update: public ArchiveState<Update> {
	Server::entity_id_type entity_id;
	Update( Server::entity_id_type ent_id = 0 ):
		entity_id( ent_id )
	{}
	
	using ArchiveState<Update>::serialize;
	using ArchiveState<Update>::deserialize;

	template< class Archive >
	void serialize( Archive& ar, const unsigned int version ) {
		ar & entity_id;
	}
};

struct Connection: public ArchiveState<Connection> {
	enum PacketType { 
		Connecting, InitializeUDP, BaselineData, Connected, NoType
	};
	PacketType type;

	union DataType {
		struct { unsigned short ping, port; } initialize_udp;
		struct { Server::entity_id_type entity_id; } connected;
	} data;

	Connection( PacketType t = NoType ): type( t )
	{}

	using ArchiveState<Connection>::serialize;
	using ArchiveState<Connection>::deserialize;

	template< class Archive >
	void serialize( Archive& ar, unsigned short version ) {
		ar & type;
		switch( type ) {
			case InitializeUDP:
				ar & data.initialize_udp.ping;
				ar & data.initialize_udp.port;
				break;
			case Connected:
				ar & data.connected.entity_id;
				break;
			default:
				break;
		};
	}
};

void ClientData::reliable_connect( const std::string& baseline,
		state_ptr_type input ) {

	baseline_data = baseline;
	input_state = input;

	ip::tcp::endpoint ep = reliable_socket.remote_endpoint();
	address = ep.address().to_v4().to_ulong();
	port = ep.port();

	reliable_socket.async_read_some( buffer(reliable_buffer, 1024),
		boost::bind( &ClientData::handle_rel_recv, this,
			placeholders::error, placeholders::bytes_transferred ) );
}

void ClientData::connect( ip::udp::endpoint remote_endpt ) {
	if( !socket.is_open() ) {
		socket.connect( remote_endpt );
		socket.async_receive( buffer( output_buffer ),
			boost::bind( &ClientData::handle_recv, this,
				placeholders::error,
				placeholders::bytes_transferred )
			);
	}

	if( socket.remote_endpoint() == remote_endpt ) {
		ip::udp::endpoint ep = socket.local_endpoint();
		std::string data( (const char*)ep.data(), ep.capacity() );
		add_data( data );
		send();
	}
}

void ClientData::handle_rel_recv( const error_type& err, size_t bytes ) {
	if( err ) {
		if( err.value() == 10054 ) {
			std::cout << "Client disconnected." << std::endl;
		} else {
			std::cout << "Receive error: " << err.value();
			std::cout << " " << err.category().name() << std::endl;
		}
	} else {
		Header header;
		std::string s( reliable_buffer.data(), bytes );
		s = header.deserialize( s );
		std::cout << bytes << " " << header.length << std::endl;

		if( connecting ) 
			handle_connecting_recv( s );

		reliable_socket.async_read_some( buffer(reliable_buffer, 1024),
			boost::bind( &ClientData::handle_rel_recv, this,
				placeholders::error, placeholders::bytes_transferred ) );
	}
}

void ClientData::handle_connecting_recv( std::string& s ) {
	Connection connection;
	s = connection.deserialize( s );
	std::cout << "Connecting ";
	std::cout << (unsigned short)connection.type << std::endl;

	switch( connection.type ) {
	case Connection::Connecting: {
		add_rel_data( connection.serialize() );
		break;
	}
	case Connection::InitializeUDP: {
		add_rel_data( connection.serialize() );
		break;
	}
	case Connection::BaselineData: {
		std::string d = connection.serialize() + baseline_data;
		add_rel_data( d );
		break;
	}
	case Connection::Connected: {
		connecting = false;
		AcquirePythonGIL gil;
		connection.data.connected.entity_id = input_state->entity_id;
		add_rel_data( connection.serialize() );
		break;
	}
	default:
		break;
	}

	rel_send();
}

void ClientData::handle_rel_send( const error_type& err, size_t bytes ) {
}

void ClientData::handle_recv( const error_type& err, size_t bytes ) {
	if( err ) {
		if( err.value() == 10061 ) {
			std::cout << "Receive error: connection problems." << std::endl;
		} else {
			std::cout << "Receive error: " << err.value();
			std::cout << " " << err.category().name() << std::endl;
		}
	} else {
		std::string s( output_buffer.data(), bytes );
		Header header(0);
		s = header.deserialize( s );

		//std::cout << "Recv" << std::endl;
		AcquirePythonGIL gil;
		input_state->deserialize( s );
		//std::cout << "Recv!" << std::endl;

		socket.async_receive( buffer( output_buffer ),
			boost::bind( &ClientData::handle_recv, this,
				placeholders::error,
				placeholders::bytes_transferred )
			);
	}
}

void ClientData::handle_send( const error_type& err, size_t bytes ) {
}

void ClientData::send() {
	Header header( output_data.length() );
	output_data = header.serialize() + output_data;
	socket.async_send( buffer( output_data ),
		boost::bind( &ClientData::handle_send, this, 
			placeholders::error, placeholders::bytes_transferred ) );
}

void ClientData::rel_send() {
	Header header( reliable_data.length() );
	reliable_data = header.serialize() + reliable_data;
	reliable_socket.async_send( buffer( reliable_data ),
		boost::bind( &ClientData::handle_rel_send, this, 
			placeholders::error, placeholders::bytes_transferred ) );
}

Server::Server( double dt_, connect_cb_type conn, new_entity_cb_type ne ): 
	dt( dt_ ), connect_cb( conn ), new_entity_cb( ne ),
	sock( service, udp::endpoint(udp::v4(), 1324) ),
	acceptor( service, tcp::endpoint(tcp::v4(), 1325) ),
	timer( service, boost::posix_time::microseconds( size_t(dt*1000000) ) ) 
{
	start_accept();
	sock.async_receive_from(
		buffer( recv_buffer ), remote_endpt,
		boost::bind( &Server::handle_accept, this,
			placeholders::error, placeholders::bytes_transferred )
		);

	timer.async_wait( 
		boost::bind( &Server::handle_tick, this,
			placeholders::error )
		);
}

void Server::start_accept() {
	client_ptr_type c( new ClientData( acceptor.get_io_service() ) );
	acceptor.async_accept( c->reliable_socket,
		boost::bind( &Server::handle_rel_accept, this, c,
			placeholders::error ) );
}

void Server::handle_accept( const error_type& err, size_t bytes ) {
	if( err ) {
		
	} else {
		std::cout << "Accept " << remote_endpt << std::endl;

		Header header;
		std::string s( recv_buffer.data(), bytes );
		s = header.deserialize( s );

		ip::tcp::endpoint ep;
		std::memcpy( ep.data(), s.c_str(), ep.capacity() );

		client_data_type::iterator it = client_data.begin();
		for( ; it != client_data.end(); ++it ) {
			if( !(*it)->connecting ) continue;
			if( (*it)->reliable_socket.remote_endpoint() == ep )
				(*it)->connect( remote_endpt );
		}
	}

	sock.async_receive_from(
		buffer( recv_buffer ), remote_endpt,
		boost::bind( &Server::handle_accept, this,
			placeholders::error, placeholders::bytes_transferred )
		);
}

void Server::handle_rel_accept( client_ptr_type c, const error_type& err ) {
	if( err ) {

	} else {
		std::cout << "RelAccept ";
		std::cout << c->reliable_socket.remote_endpoint() << std::endl;
		client_data.push_back( c );

		std::string baseline_data;

		AcquirePythonGIL gil;
		ClientInfo info( c->reliable_socket.remote_endpoint() );
		state_ptr_type input_state = connect_cb( info );

		entity_state_type::iterator i = entity_states.begin();
		for( ; i != entity_states.end(); ++i ) {
			baseline_data += Update( i->first ).serialize();
			baseline_data += new_entity_cb( i->second );
		}
		c->reliable_connect( baseline_data, input_state );
	}

	start_accept();
}

void Server::handle_tick( const Server::error_type& err ) {
	{
		AcquirePythonGIL gil;
		entity_state_type::iterator ei = entity_states.begin(); 
		for( ; ei != entity_states.end(); ++ei ) {
			//std::cout << "Tick " << ei->first << std::endl;
			std::string data = Update( ei->first ).serialize();
			data += ei->second->serialize();
			//std::cout << "Tick!" << std::endl;

			client_data_type::iterator in = client_data.begin();

			switch( ei->second->routing ) {
			case State::All:
			case State::PotentiallyVisible:
				for( ; in != client_data.end(); ++in )
					(*in)->add_data( data );
				break;
			case State::Others:
				for( ; in != client_data.end(); ++in )
					if( (*in)->network_id != ei->second->network_id )
						(*in)->add_data( data );
				break;
			case State::Single:
				for( ; in != client_data.end(); ++in )
					if( (*in)->network_id == ei->second->network_id )
						(*in)->add_data( data );
				break;
			}
		}
	}

	client_data_type::iterator in = client_data.begin();
	for( ; in != client_data.end(); ++in )
		(*in)->send();

	timer.expires_at( timer.expires_at() + 
		boost::posix_time::microseconds( size_t(dt*1000000) ) );
	timer.async_wait( boost::bind( &Server::handle_tick, this,
		placeholders::error ) );
}

void Server::do_update( state_ptr_type s ) {
	AcquirePythonGIL gil;
	if( !entity_states.count( s->entity_id ) ) {
		std::cout << "New ent" << std::endl;
		std::string rel_data;
		{
			rel_data += Update( s->entity_id ).serialize();
			rel_data += new_entity_cb( s );
		}

		client_data_type::iterator in = client_data.begin();
		for( ; in != client_data.end(); ++in ) {
			(*in)->add_rel_data( rel_data );
			(*in)->rel_send();
		}
		std::cout << "New ent!" << std::endl;
	}

	entity_states[ s->entity_id ] = s;
	s.reset();
}

void Server::do_run() {
	try {
		service.run();
	} catch( boost::python::error_already_set const & ) {
		std::cout << "Exception" << std::endl;
		AcquirePythonGIL gil;
		PyErr_Print();
	}
};

void Server::update( state_ptr_type s ) {
	service.post( boost::bind( &Server::do_update, this, s ) );
}

void Server::run() {
	PyEval_InitThreads();
	AcquirePythonGIL gil;
	thread = boost::thread( boost::bind( &Server::do_run, this ) );
}

void Server::stop() {
	timer.cancel();
	sock.cancel();
	thread.join();
}

Client::Client( double dt_, new_entity_cb_type new_ent ):
	new_entity_cb( new_ent ), dt(dt_), connecting( false ), 
	sock( service, udp::endpoint( udp::v4(), 0 ) ),
	reliable_sock( service, tcp::endpoint( tcp::v4(), 0 ) ),
	timer( service ) 
{}

void Client::connect( const std::string& host, const std::string& port,
		const std::string& reliable_port, connect_cb_type callback ) {

	timer.expires_from_now( 
		boost::posix_time::microseconds( size_t(dt*1000000) ) );
	timer.async_wait( boost::bind( &Client::handle_tick, this, 
		placeholders::error ) );

	connecting = true;
	connect_cb = callback;

	udp::resolver resolver( service );
	udp::resolver::query query( udp::v4(), host, port );
	udp::resolver::iterator i = resolver.resolve( query );
	server_endpt = *i;		

	sock.async_receive( buffer(recv_buffer),
		boost::bind( &Client::handle_recv, this,
			placeholders::error, placeholders::bytes_transferred ) );

	tcp::resolver rel_resolver( service );
	tcp::resolver::query rel_query( tcp::v4(), host, reliable_port );
	async_connect( reliable_sock, rel_resolver.resolve( rel_query ),
		boost::bind( &Client::handle_connect, this,
		  	placeholders::error ) );
}

void Client::handle_connect( const error_type& error ) {
	Connection conn( Connection::Connecting );
	do_rel_send( conn.serialize() );

	reliable_sock.async_read_some( 
		buffer(reliable_buffer, 1024),
		boost::bind( &Client::handle_rel_recv, this,
			placeholders::error, placeholders::bytes_transferred ) );
}

void Client::handle_rel_recv( const error_type& error, size_t bytes ) {
	if( error ) {

	} else {
		Header header;
		std::string s( reliable_buffer.data(), bytes );
		s = header.deserialize( s );
		std::cout << bytes << " " << header.length << std::endl;

		if( !connecting ) {
			s = do_rel_updates( s );
		} else {
			Connection connection;
			s = connection.deserialize( s );
			std::cout << "Connecting " << (unsigned short)connection.type <<
				std::endl;

			switch( connection.type ) {
			case Connection::Connecting: {
				ip::tcp::endpoint ep = reliable_sock.local_endpoint();
				std::string data( (const char*)ep.data(), ep.capacity() );
				do_send( data );

				Connection conn( Connection::InitializeUDP );
				do_rel_send( conn.serialize() );
				break;
			}	
			case Connection::InitializeUDP: {
				Connection conn( Connection::BaselineData );
				do_rel_send( conn.serialize() );
				break;
			}
			case Connection::BaselineData: {
				s = do_rel_updates( s );
				Connection conn( Connection::Connected );
				do_rel_send( conn.serialize() );
				break;
			}
			case Connection::Connected: {
				connecting = false;
				AcquirePythonGIL gil;
				connect_cb( connection.data.connected.entity_id );
				break;
			}
			}
		}
	}

	reliable_sock.async_read_some( buffer(reliable_buffer, 1024),
		boost::bind( &Client::handle_rel_recv, this,
			placeholders::error, placeholders::bytes_transferred ) );
}

void Client::handle_rel_send( const error_type& error, size_t bytes ) {

}

void Client::handle_recv( const error_type& error, size_t bytes ) {
	//std::cout << "Recv" << std::endl;
	std::string s( recv_buffer.data(), bytes );
	Header header(0);
	s = header.deserialize( s );

	if( connecting ) {
		unsigned char* ep = (unsigned char*)server_endpt.data();
		std::memcpy( ep, s.c_str(), server_endpt.capacity() );
		std::cout << "Got " << server_endpt << std::endl;
	} else {
		Update update;
		AcquirePythonGIL gil;

		while( s.length() ) {
			s = update.deserialize( s );
			if( !entity_states.count( update.entity_id ) ) 
				break;
			s = entity_states[ update.entity_id ]->deserialize( s );
		}
	}

	sock.async_receive( buffer(recv_buffer),
		boost::bind( &Client::handle_recv, this,
			placeholders::error, placeholders::bytes_transferred ) );
	//std::cout << "Recv!" << std::endl;
}

void Client::handle_send( const error_type& error, size_t bytes ) {

}

void Client::handle_tick( const error_type& error ) {
	//std::cout << "Ticking" << std::endl;
	if( connecting ) {

	} else if( input_state ) {
		AcquirePythonGIL gil;
		do_send( input_state->serialize() );
	}

	timer.expires_at( timer.expires_at() + 
		boost::posix_time::microseconds( size_t(dt*1000000) ) );
	timer.async_wait( boost::bind( &Client::handle_tick, this,
		placeholders::error ) );
	//std::cout << "Ticking!" << std::endl;
}

void Client::do_send( const std::string& data ) {
	Header header( data.length() );
	input_data = header.serialize() + data;

	sock.async_send_to( 
		buffer( input_data ), server_endpt,
		boost::bind( &Client::handle_send, this,
			placeholders::error, placeholders::bytes_transferred ) );
}

void Client::do_rel_send( const std::string& data ) {
	Header header( data.length() );
	rel_data = header.serialize() + data;

	reliable_sock.async_send( buffer( rel_data, rel_data.length() ),
		boost::bind( &Client::handle_rel_send, this,
			placeholders::error, placeholders::bytes_transferred ) );
}

std::string& Client::do_rel_updates( std::string& s ) {
	Update update;
	AcquirePythonGIL gil;

	while( s.length() ) {
		s = update.deserialize( s );
		NewEntityData data = new_entity_cb( s );
		entity_states[update.entity_id] = data.state;
		data.state->entity_id = update.entity_id;
		s = data.data;
	}

	return s;
}

void Client::do_input( state_ptr_type state ) {
	AcquirePythonGIL gil;
	input_state = state;
	state.reset();
}

void Client::do_run() {
	try {
		service.run();
	} catch( boost::python::error_already_set ) {
		std::cout << "Exception" << std::endl;
		AcquirePythonGIL gil;
		PyErr_Print();
	}
};

void Client::input( state_ptr_type ent ) {
	service.post( boost::bind( &Client::do_input, this, ent ) );
}

void Client::run() {
	PyEval_InitThreads();
	AcquirePythonGIL gil;
	thread = boost::thread( boost::bind( &Client::do_run, this ) );
}

void Client::stop() {
	timer.cancel();
	sock.cancel();
	thread.join();
}


