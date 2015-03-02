#include <sstream>
#include <iostream>
#include <fstream>
#include "socketHelper.h"

#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

int main(int argc, char* argv[]) { 

    const char * host = "127.0.0.1";
    struct hostent *server;
    int port = 8000;

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;

    server = gethostbyname(host);
    bcopy((char *)server->h_addr, 
        (char *)&serv_addr.sin_addr.s_addr,
        server->h_length);
    serv_addr.sin_port = htons(port);

    if (connect(sockfd,(const sockaddr*)&serv_addr,sizeof(serv_addr)) < 0)
        error("ERROR connecting");


    std::string mesg = recv_msg(sockfd);
    std::string action;
    std::cout << mesg;
    getline (std::cin, action);
    long id = 0;

    if (action.compare("new")==0){
        send_msg(sockfd, action);
        id = std::stol (recv_msg(sockfd));
        std::cout << id << std::endl;
    }
    else{
        send_msg(sockfd, action);
    }

    std::cout << "Action(update/delete)? -> ";
    getline (std::cin, action);
    send_msg(sockfd, action);

    std::string filePath;
    std::cout << "Json file path to use for update/delete? -> ";
    getline (std::cin, filePath);

    std::ifstream ifs(filePath);
    std::string fileContent( (std::istreambuf_iterator<char>(ifs) ),
                       (std::istreambuf_iterator<char>()    ) );
    send_msg(sockfd, fileContent);

    std::string serverData = recv_msg(sockfd);

    std::cout << serverData << std::endl;
    close(sockfd);
	return 0;
}

