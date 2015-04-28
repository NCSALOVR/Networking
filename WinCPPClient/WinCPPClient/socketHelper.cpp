#include <sstream>
#include <iostream>
#include <fstream>
#include <stdexcept>

#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <stdlib.h>
#include <stdio.h>

#include <cstdint>
#include "socketHelper.h"


SOCKET setupClientSocket(const char * host, const char * port){
	WSADATA wsaData;
	struct addrinfo *result = NULL,
		*ptr = NULL,
		hints;
	int iResult;
	SOCKET ConnectSocket = INVALID_SOCKET;

	SecureZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = 0;

	iResult = getaddrinfo(host, port, &hints, &result);
	if (iResult != 0){
		printf("getaddrinfo failed: %d\n", iResult);
		return ConnectSocket;
	}

	for (ptr = result; ptr != NULL; ptr = ptr->ai_next) {

		// Create a SOCKET for connecting to server
		ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype,
			ptr->ai_protocol);
		if (ConnectSocket == INVALID_SOCKET) {
			printf("socket failed with error: %ld\n", WSAGetLastError());
			return ConnectSocket;
		}

		// Connect to server.
		iResult = connect(ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
		if (iResult == SOCKET_ERROR) {
			closesocket(ConnectSocket);
			ConnectSocket = INVALID_SOCKET;
			continue;
		}
		break;
	}

	freeaddrinfo(result);

	if (ConnectSocket == INVALID_SOCKET) {
		printf("Unable to connect to server!\n");
		return ConnectSocket;
	}
	return ConnectSocket;
}


void sendMsg(SOCKET sockfd, std::string msg){
	const char* cMsg = msg.c_str();
	size_t length = strlen(cMsg);
	uint32_t nlength = htonl(length);
	//send the length (i.e., number of bytes) of the message
	send(sockfd, (char*)&nlength, 4, 0);
	//send the actual message
	send(sockfd, cMsg, length, 0);
}

std::string recvMsg(SOCKET sockfd){
	uint32_t length, nlength;

	int num_bytes_recv = 0;
	int curr_num_bytes_recv;

	//getting the first 4 bytes, which store number of bytes of the msg
	while (num_bytes_recv < 4){
		curr_num_bytes_recv = recv(sockfd, ((char*)&nlength) + num_bytes_recv, 4 - num_bytes_recv, 0);
		if (curr_num_bytes_recv == 0){
			return "";
		}
		if (curr_num_bytes_recv == SOCKET_ERROR){
			throw std::runtime_error("receive nothing");
		}
		num_bytes_recv += curr_num_bytes_recv;
	}
	
	length = ntohl(nlength);
	return recvNumBytes(sockfd, length);
}

std::string recvNumBytes(SOCKET sockfd, uint32_t num_bytes){
	char* data = (char*)malloc(num_bytes + 1);
	data[num_bytes] = '\0';
	uint32_t num_bytes_recv = 0;
	uint32_t curr_num_bytes_recv;

	//loop until we recieve all the num_bytes
	while (num_bytes_recv < num_bytes){
		curr_num_bytes_recv = recv(sockfd, data + num_bytes_recv, num_bytes - num_bytes_recv, 0);
		num_bytes_recv += curr_num_bytes_recv;
	}
	return std::string(data);
}
