#include <sstream>
#include <iostream>
#include <fstream>
#include <stdexcept>

#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <stdlib.h>
#include <stdio.h>

#pragma comment (lib, "Ws2_32.lib")
#pragma comment (lib, "Mswsock.lib")
#pragma comment (lib, "AdvApi32.lib")

#include <thread>
#include "socketHelper.h"
#include "threadClient.h"


int main(int argc, char* argv[]) {

	const char * host = "127.0.0.1";
	int port = 8000;

	//setting up and initialize winsock
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 0), &wsaData) != 0)
	{
		fprintf(stderr, "WSAStartup() failed");
		exit(1);
	}

	//registration
	std::string action;
	std::cout << "Registration ('new'/your id/'end'): ";
	getline(std::cin, action);

	//getting update interval
	float t = 1.0;
	std::string interval;
	std::cout << "Interval between updates(seconds): ";
	getline(std::cin, interval);
	try{
		t = std::stof(interval);
	}
	catch (std::exception& e){
		std::cout << "Standard exception: " << e.what() << std::endl;
		std::cout << "Interval set to default value of 1" << std::endl;
	}

	begin(action, t);
	std::thread tWrite(threadCtoS);
	std::thread tRead(threadStoC, t);

	while (true){

		std::string update = getUpdate();
		if (update.length() != 0){
			std::cout << update << std::endl;
		}

		std::string action;
		std::cout << "Action(update/delete/end)? -> ";
		getline(std::cin, action);
		std::string data = "";

		if (action.compare("end") == 0){
			sendCommand(action, data);
			tWrite.join();
			tRead.join();
			break;
		}

		if (action.compare("update") == 0 || action.compare("delete") == 0){

			std::string filePath;
			std::cout << "Json file path to use for update/delete? -> ";
			getline(std::cin, filePath);

			std::ifstream ifs(filePath, std::ifstream::in);
			if (ifs.is_open()){
				data.assign((std::istreambuf_iterator<char>(ifs)), (std::istreambuf_iterator<char>()));
				ifs.close();
			}
			else{
				std::cout << "Not a valid file: " << filePath << std::endl;
				continue;
			}
		}
		sendCommand(action, data);
	}
	WSACleanup();
}