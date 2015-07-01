
#ifndef KDTREE_H
#define KDTREE_H

#include "math.h"
#include <boost/shared_ptr.hpp>

template< class T >
class kdTreeNode {
public:

	bool leaf;
	shared_ptr<kdTreeNode> parent;

	const static size_t split_points = 25;

	union {
		struct {
			shared_ptr<kdTreeNode> left, right;
			int axis;
		} node;

		struct {
			vector< pair<Vector2f,T> > points;
		} leaf;
	} data;

	kdTreeNode( ): leaf( true )
	{}

	kdTreeNode( shared_ptr<kdTreeNode> parent_, vector< pair<Vector2f,T> >& points_ ) {
		initialize( parent_, points_ );
	}

	void initialize( shared_ptr<kdTreeNode> parent_, vector< pair<Vector2f,T> >& points_ ) {
		parent = parent_;

		if( points_.size() > split_points ) {
			leaf = false;

			data.node.axis = (parent->axis+1)%2;
		}
	}


}

class kdTree: public kdTreeNode {

	shared_ptr< kdTreeNode > root;

	kdTree( vector< pair<Vector2f,T> >& points_ ): axis(0) {
		root = shared_ptr< kdTreeNode >( new kdTreeNode( shared_from_this( this ), points_ ) );
	}

};



#endif