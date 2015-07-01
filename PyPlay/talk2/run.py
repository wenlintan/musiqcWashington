import knowledge, parse, commands

print "Beginning processing..."
know = knowledge.knowledge()
pars = parse.parser( know )
comm = commands.commands( know, pars )

while True:
    data = raw_input(">>>")
    res = comm( data )
    
    if res:
        if res < 0:
            break
        continue

    #else process as usual
    pars( data )
    
