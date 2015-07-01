
import pdb

class conjugate_gradient_solver:
    def __init__( self, threshold = 1e-8, max_iterations = 100, x0 = None ):
        self.x0 = x0
        self.threshold = threshold
        self.max_iterations = max_iterations
        
    def solve( self, A, b ):
        x = self.x0
        if x is None:
            x = full_matrix( [[0.0]] * A.n )
 
        r = b - A*x
        p = r

        iterations = 0
        while iterations < self.max_iterations:
            rmag = r.transpose()*r
            alpha = rmag / (p.transpose()*A*p)
            x = x + p*alpha
            r = r - A*p*alpha

            if abs(rmag) < self.threshold:
                break

            beta = r.transpose()*r / rmag
            p = r + p*beta
            iterations += 1

        return x
            
        
class matrix(object):
    solver = conjugate_gradient_solver()
    def __init__( self, n, m ):
        self.n, self.m = n, m

    def __add__( self, other ):
        pass
    
    def __mul__( self, vec ):
        pass

    def transpose( self ):
        pass

    def solve( self, b ):
        return self.solver.solve( self, b )

class vector_matrix( matrix ):
    def __init__( self, n, m, data ):
        super( vector_matrix, self ).__init__( n, m )
        self.data = data

    

class full_matrix( matrix ):
    def __init__( self, data, n = None, m = None ):
        if n is None:
            n, m = len(data), len(data[0])
            
        super( full_matrix, self ).__init__( n, m )
        self.data = data

    def rows( self ):
        return [full_matrix([x,], 1, self.m) for x in self.data]

    def cols( self ):
        return [full_matrix([[x,] for x in c], self.n, 1)
                for c in zip(*self.data)]
    
    def __add__( self, other ):
        assert self.n == other.n and self.m == other.m
        g = [[x+y for x,y in zip(r1, o1)]
             for r1, o1 in zip(self.data, other.data)]
        return full_matrix( g, self.n, self.m )

    def __sub__( self, other ):
        assert self.n == other.n and self.m == other.m
        g = [[x-y for x,y in zip(r1, o1)]
             for r1, o1 in zip(self.data, other.data)]
        return full_matrix( g, self.n, self.m )

    def __mul__( self, other ):
        if isinstance( other, float ):
            g = ((other*x for x in row) for row in self.data)
            return full_matrix( g, self.n, self.m )

        assert self.m == other.n            
        if self.n == 1 and other.m == 1:
            return sum( x*y[0] for x,y in zip(self.data[0], other.data) )

        data = [[x*y for y in other.cols()] for x in self.rows()]
        return full_matrix( data, self.n, other.m )

    def transpose( self ):
        return full_matrix( [x for x in zip(*self.data)], self.m, self.n )

    def __str__( self ):
        return str([[x for x in row] for row in self.data])
    
class csr_matrix( matrix ):
    def __init__( self, width, row_starts, cols, vals ):
        super( csr_matrix, self ).__init__( len(row_starts), width )
        self.rows = row_starts
        self.cols, self.vals = cols, vals    
        
if __name__ == "__main__":
