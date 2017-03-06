# Routing-Table

In	this	project	you	will	learn	about	router	behavior	by building another	server	using	
Python	sockets,	but	rather	than	a	web	server,	this	one	will	handle two	kinds	messages:
- First,	it	can	receive messages	(UPDATE)	updating	routing	information (in	a	sort	of	
simplified	version	of	BGP).
- Second,	it	can	receive questions	(QUERY) asking	your	server	where	it would	route	a	
message (Note	that	in	reality,	that	wouldn’t	happen	– the	router	would just receive
packets	and route them,	but	for	our	exercise	it will	instead	reply	to	messages	asking	
“where” instead).

![Routing-Table](/test.png "step 1")
![Routing-Table](/server.png "step 2")	
