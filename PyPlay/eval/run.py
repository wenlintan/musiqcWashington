import interpret as i

inter = i.interpreter()

lit = 0
addargs = ["mov", -1, -2, "add", -1, lit, 1, "add", -5, -6, "ret", -1]
selfmod = ["mov", -1, -2, "inc", -1, "mov", -1, -3,
           "inc", -1, "mov", -5, 29, "jne", 29, lit, "div", lit, 28,
           "jne", -7, lit, 0, lit, 28, "ret", lit, 0, 1000, -6, -7,
           "ret", -1]
args = [15, 3, "div"]

try:
    ret = inter.evaluate( selfmod, args )
    print ret
except i.evaluate_error, e:
    print "Interpret error: " + e.desc
    
