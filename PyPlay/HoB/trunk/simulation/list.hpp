
#include <cstddef>

template< typename T >
struct ListLink;

template< typename T, ListLink<T> T::*member >
class List;

template< typename T >
struct ListMemberHelper {
	typedef ListLink<T> T::*accessor;
	const static accessor m;
};

template< typename T >
const typename ListMemberHelper<T>::accessor 
	ListMemberHelper<T>::m = &T::links;

template< typename T >
struct ListLink {
	ListLink<T>(): prev( 0 ), next( 0 )
	{}

	ListLink<T>( ListLink<T>* prev_, ListLink<T>* next_ ):
		prev( prev_ ), next( next_ ) 
	{}

	~ListLink() {
		prev->next = next;
		next->prev = prev;
	}

	void link( ListLink<T>* previous ) {
		prev = previous;
		next = previous->next;

		previous->next->prev = this;
		previous->next = this;
	}
		
	ListLink<T>	*prev, *next;
};


template< typename T, ListLink<T> T::*member >
class ListIterator {
	friend class List<T, member>;
	ListLink<T>*	current;

	typedef ListIterator<T, member> this_type;
	typedef const ListIterator<T, member> const_this_type;

	std::ptrdiff_t offset_from_pointer_to_member() {
		const T* const parent = 0;
		const char* const member_ptr = reinterpret_cast<const char*>(
			&(parent->*member) );
		return std::ptrdiff_t( member_ptr
			 - reinterpret_cast<const char*>(parent) );
	}

	T* get_element( ListLink<T>* links ) {
		return reinterpret_cast<T*>( (char*)links - 
			offset_from_pointer_to_member() );
	}

public:
	ListIterator<T, member>(): current(0)
	{}

	ListIterator<T, member>( ListLink<T>& pos ): current( &pos )
	{}

	ListIterator<T, member>& operator++() {
		current = current->next;
		return *this;
	}

	ListIterator<T, member> operator++(int) {
		this_type ans = *this;
		++(*this);
		return ans;
	}

	ListIterator<T, member>& operator--() {
		current = current->prev;
		return *this;
	}

	T& operator*() 		{ return *get_element( current ); }
	T* operator->()		{ return &operator*(); }

	friend bool operator==( const_this_type& lhs, const_this_type& rhs ) {
		return lhs.current == rhs.current;
	}

	friend bool operator!=( const_this_type& lhs, const_this_type& rhs ) {
		return lhs.current != rhs.current;
	}
};


template< typename T, ListLink<T> (T::*member) >// = ListMemberHelper<T>::m >
class List {
	ListLink< T >	link;

public:
	typedef T value_type;
	typedef ListIterator< T, member > iterator;

	List<T, member>():
		link( &link, &link )
	{}

	~List<T, member>() {
		iterator i = begin(), e = end();
		while( i != e ) {
			T* p = &*i++;
			delete p;
		}
	}

	List<T, member>& push_back( T* elem ) {
		(elem->*member).link( link.prev );
		return *this;
	}

	T& front() 	{ return *begin(); }
	T& back() 	{ return *--end(); }

	iterator begin() 	{ return iterator( *link.next ); }
	iterator end()		{ return iterator( link ); }
	
};
