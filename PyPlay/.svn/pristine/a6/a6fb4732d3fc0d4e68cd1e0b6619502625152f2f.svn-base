import math

def gen():
    for n in range(1, 501):
        hn = 0
        for i in range(1, n+1):
            hn += math.log(i)

        n2logn = n**2 * math.log(n)
        nlognminn = n * math.log(n) - n
        print "n=%d -> Hn=%f, Hn-(nlog(n)-n)=%f"% ( n,
                                                    hn,
                                                    hn - nlognminn )

gen()
                                                 
