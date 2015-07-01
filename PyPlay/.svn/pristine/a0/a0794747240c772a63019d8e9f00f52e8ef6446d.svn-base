struct GRBNoData {
	typedef boost::tuples::null_type list;
};

template< typename DT1 >
class GRBDataManager1 {
	typedef DT1 head;
	typedef GRBNoData tail;
	typedef boost::tuples::cons< head, boost::tuples::null_type > list;
};

template< typename DT1, typename DT2 >
class GRBDataManager2 {
	typedef DT1 head;
	typedef GRBDataManager1<DT2> tail;
	typedef boost::tuples::cons< head, typename GRBDataManager1<DT2>::list > list;
};

template< typename DT1, typename DT2 >
class GRBDataManager {
public:
	typedef GRBDataManager2< DT1, DT2 > type;
	GRBDataManager< DT1, DT2 >( typename type::list l ): c_data( l )
	{ }

	template< size_t n >


	template< typename ConvertType >
	typename ConvertType convert() {
		return ConvertType( convert<ConvertType::type, type>( c_data ) )
	}

private:
	template< typename ConvertType, typename DataType >
	typename ConvertType::list convert_internal( typename DataType::list data ) {
		return ConvertType::list(	
			GRBDataConverter< ConvertType::head, DataType::head >( data.car ),
			convert_internal< ConvertType::tail, DataType::tail >( data.cdr ) 
			);
	}

	template<>
	typename GRBNoData::list convert_internal< GRBNoData, GRBNoData >( typename GRBNoData::list data ) {
		return boost::tuples::null_type();
	}

	typename type::list	c_data;
};

template< typename DT1 >
class GRBDataManager< DT1, GRBNoData > {
	typedef GRBDataManager1< DT1 > type;
};

template<>
class GRBDataManager< GRBNoData, GRBNoData >  {
	typedef GRBNoData type;
};