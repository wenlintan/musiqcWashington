
/*
        shelves = []
        m, r = masses[i], rabi_freqs[i]
        etas = [ numpy.sqrt( hbar / 2 / m / amu / w ) * 2 * numpy.pi / 
            1.762e-6 / numpy.sqrt(2) for w in ws ]

        for t in times:
            totalprob, res = 0.0, 0.0
            nsamples = 1000
            for sample in range( nsamples ):
                ns = [ random.randint(0, 1000) for i in range(2*nions) ]
                prob, freq = 1.0, 1.0
                for j, n, nb, eta in zip( range(2*nions), ns, nbars, etas ):
                    v = vs[i,j]
                    prob *= 1 / (float(nb)+1) * (float(nb) / (nb+1))**n
                    freq -= eta**2 * v**2 * n
                totalprob += prob
                res += prob * numpy.cos( 2*r*freq*t )   
            res /= totalprob
            shelves.append( s * (1 - res) )
        output.append( numpy.array(shelves) )
        */

#include <iostream>
#include <vector>

#include <random>
#include <cmath>

#include <boost/thread.hpp>
#include <boost/bind.hpp>

const double hbar = 1.055e-34;
const double pi = 3.141592654;

struct SampleThread {
    SampleThread( size_t seed, size_t nions_, double s_, 
            double* ws_, double* vs_, double* nbars_ ): 
        generator(seed), 
        distr(0, 1500), 
        nions(nions_), s(s_), ws(ws_), 
        vs(vs_), nbars(nbars_) {}

    void operator()( size_t nsamples, size_t i,
            double m, double r, double t, double* etas ) {

        prob = 0.0;
        double totalprob = 0.0, totalvalue = 0.0;
        for( size_t samp = 0; samp < nsamples; ++samp ) {

            double prob = 1.0, freq = 1.0;
            for( size_t mode = 0; mode < 2*nions; ++mode ) {
                size_t n = distr( generator );
                double nbar = nbars[ mode ];
                double v = vs[i*2*nions + mode];

                prob *= 1. / (nbar+1) * pow( (nbar / (nbar+1)), n );
                freq -= etas[mode]*etas[mode] * v * v * n;
            }
            totalprob += prob;
            totalvalue += prob * cos( 2*r*freq*t );
        }

        //std::cout << totalprob << ", " << totalvalue << std::endl;
        prob = s * (1. - totalvalue / totalprob);

    }

    std::default_random_engine generator;
    std::uniform_int_distribution<int> distr;

    size_t nions;
    double s;
    double *ws, *vs, *nbars;
    double prob;
};

#ifdef WINDOWS
#define EXPORT __declspec(dllexport) 
#else
#define EXPORT
#endif

extern "C" EXPORT void rabi_flop( 
    size_t nsamples, size_t nions, size_t ntimes, double s, 
    double* masses, double* rabi_freqs, 
    double* ws, double* vs, double* nbars, 
    double* times, double* result ) {

    bool debug = false;
    if( debug ) {
        std::cout << nions << " Ions" << std::endl;
        std::cout << ntimes << " Times" << std::endl; 
        std::cout << "Scale: " << s << std::endl << std::endl;    
        
        for( size_t i = 0; i < nions; ++i ) {
            std::cout << "Mass: " << masses[i] << std::endl;
            std::cout << "Rabi: " << rabi_freqs[i] << std::endl;
        }

        std::cout << std::endl << "Modes:" << std::endl;
        for( size_t m = 0; m < 2*nions; ++m ) {
            std::cout << "Freq: " << ws[m] << std::endl;
            std::cout << "Nbar: " << nbars[m] << std::endl;
            std::cout << "Vec: ";
            for( size_t i = 0; i < nions; ++i ) 
                std::cout << vs[i*2*nions + m] << ", ";
            std::cout << std::endl;
        }
    }

    const size_t nthreads = 4;

	std::vector< SampleThread* > thread_data;
	for( size_t i = 0; i < nthreads; ++i )
		thread_data.push_back( new SampleThread( 
            i, nions, s, ws, vs, nbars ) );

    double* etas = new double[ 2*nions ];
    for( size_t i = 0; i < nions; ++i ) {
        double m = masses[i], r = rabi_freqs[i];

        for( size_t iw = 0; iw < 2*nions; ++iw ) {
            double w = ws[iw];
            etas[iw] = sqrt( hbar / 2 / m / w ) * 2 * pi /
                1.762e-6 / sqrt(2);
        }

        for( size_t it = 0; it < ntimes; ++it ) {
            double t = times[it];
            boost::thread threads[ nthreads ];
            for( size_t thread = 0; thread < nthreads; ++thread )
                threads[thread] = boost::thread( 
                    boost::ref(*thread_data[thread]), 
                    nsamples / nthreads, i, m, r, t, etas );

            double prob = 0.;
            for( size_t thread = 0; thread < nthreads; ++thread ) {
                threads[thread].join();
                prob += thread_data[thread]->prob;
            }

            /*
            double totalprob = 0.0, totalvalue = 0.0;

            for( size_t samp = 0; samp < nsamples; ++samp ) {

                double prob = 1.0, freq = 1.0;
                for( size_t mode = 0; mode < 2*nions; ++mode ) {
                    size_t n = distr( generator );
                    double nbar = nbars[ mode ];
                    double v = vs[i*2*nions + mode];

                    prob *= 1. / (nbar+1) * pow( (nbar / (nbar+1)), n );
                    freq -= etas[mode]*etas[mode] * v * v * n;
                }
                totalprob += prob;
                totalvalue += prob * cos( 2*r*freq*t );
            }

            //std::cout << totalprob << ", " << totalvalue << std::endl;
            double value = s * (1. - totalvalue / totalprob);
            */
            result[i*ntimes + it] = prob / nthreads;
        }
    }

    delete [] etas;
	for( size_t i = 0; i < nthreads; ++i )
		delete thread_data[i];

}

