Networking
==========

The fileServer folder include the python version of server and client.  
Note that while python client is working, it is a prototype version and is not actually used in VIVE; see the C++ client.  
To run:  
Change the host variable (and possibly port variable) in the main function of server.py to the IP address (and desire port) of the server.  
Change the host global variable (and possibly port global variable) in the top of threadClient.py to the IP address (and desire port) of the server.  
=> python server.py  
=> python client.py  
  
  
The WinCPPClient folder include the Window C++ version of client; this is the client version that is used in VIVE.  
To run:  
Open WinCPPClient/WinCPPClient/WinCPPClient.vcxproj on Microsoft Visual Studio.  
Change the host global variable (and possibly port global variable) in the top of threadClient.cpp to the IP address (and desire port) of the server.  
Run it using Microsoft Visual Studio.  
  
The sampleJsonData folder include some json files; they are not necessary and are only for the testing purposes.  