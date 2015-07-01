import knowledge, langparser, commands

print "Beginning processing..."
know = knowledge.knowledge()
pars = langparser.parser( know )
com = commands.commands( know, pars )

running = True
while running:

    data = raw_input(">>>")

    res = com( data )
    if res:

        if res < 0:
            running = False
        continue

    #else process as usual
    pars( data )
    
