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
	//setting up and initialize winsock
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 0), &wsaData) != 0){
		fprintf(stderr, "WSAStartup() failed");
		exit(1);
	}

	//getting parameter action for begin()
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
	//spawn the two threads to communicate both ways with the server
	std::thread tWrite(threadCtoS);
	std::thread tRead(threadStoC, t);

	/*
	Receive the action (i.e., update/delete/end) and the file path to be used in update/delete from the terminal, and get an update from the updates queue in each iteration.
	The loop is to be replaced in the actual VIVE application to reflect the actual data to send to the server, and the actual use of data from the updates and delete queues.
	*/
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