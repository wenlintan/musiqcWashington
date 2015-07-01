
#pragma once
#include <vector>
#include <utility>

template< typename T >
struct Image {
	typedef T element;
	typedef T element_type;
	typedef T value_type;

	typedef size_t index;
	typedef size_t index_type;
	typedef std::pair< size_t, size_t > extents_type;
	typedef std::pair< size_t, size_t > position;

	extents_type		extents;
	std::vector< T >	data;
	
	Image() {}
	Image( extents_type exts ): extents( exts ),
		data( exts.first*exts.second, element() )
	{}

	template< typename List >
	Image( extents_type exts, List list ): extents( exts ), 
		data( list.begin(), list.end() )
	{}
    
	template< typename Iterator >
	Image( extents_type exts, Iterator begin, Iterator end ): 
		extents( exts ), data( begin, end )
	{}

	inline element& operator()( index i, index j ) {
		return data[ j*extents.first + i ];
	}

	inline const element& operator()( index i, index j ) const {
		return data[ j*extents.first + i ];
	}

	inline element& operator()( const position& pos ) {
		return data[ pos.second*extents.first + pos.first ];
	}

	inline const element& operator()( const position& pos ) const {
		return data[ pos.second*extents.first + pos.first ];
	}

	T* ptr() 			        { return &data[0]; }
	const T* ptr() const		        { return &data[0]; }

	index_type num_elements() const { 
		return extents.first * extents.second; 
	}
};

typedef Image< float > image_type;
typedef Image< float > edge_image_type;

