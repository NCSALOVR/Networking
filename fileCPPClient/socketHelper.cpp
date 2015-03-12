#include <sstream>
#include <iostream>
#include <fstream>
#include "socketHelper.h"
#include <sys/types.h>
#include <sys/socket.h>

void send_msg(int sockfd, std::string msg){
    const char* cMsg = msg.c_str();
    size_t length = strlen(cMsg);
    uint32_t nlength = htonl(length);
    send(sockfd, &nlength, 4, 0);
    send(sockfd, cMsg, length, 0);
}

std::string recv_msg(int sockfd){
    uint32_t length, nlength;

    //getting the first 4 bytes
    int num_bytes_recv = 0;
    int curr_num_bytes_recv;
    while(num_bytes_recv < 4){
       curr_num_bytes_recv = recv(sockfd, ((char*)&nlength)+num_bytes_recv, 4-num_bytes_recv, 0);
       num_bytes_recv += curr_num_bytes_recv;
    }

    length = ntohl(nlength);
    return recv_num_bytes(sockfd, length);
}

std::string recv_num_bytes(int sockfd, uint32_t num_bytes){
    char* data = (char*) malloc(num_bytes+1);
    data[num_bytes] = '\0';

    int num_bytes_recv = 0;
    int curr_num_bytes_recv;
    while (num_bytes_recv < num_bytes){
        curr_num_bytes_recv = recv(sockfd, data+num_bytes_recv, num_bytes-num_bytes_recv, 0);
        num_bytes_recv += curr_num_bytes_recv;
    }
    return std::string(data);
}