#include <sstream>
#include <iostream>
#include <fstream>
#include <stdexcept>

#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <stdlib.h>
#include <stdio.h>

#include <queue>
#include <tuple>
#include <thread>
#include <mutex> 

#include "socketHelper.h"
#include "threadClient.h"

long id = 0;
std::queue<std::string> updates;
std::queue<std::string> deletes;
std::queue<std::tuple<std::string, std::string>> commands;
std::mutex dataLock;
std::mutex updateLock;
const char * host = "141.142.21.57";
const char * port = "8000";

void threadCtoS(){
	updateLock.lock();
	SOCKET cToSSoc = setupClientSocket(host, port);
	if (cToSSoc == INVALID_SOCKET){
		updateLock.unlock();
		return;
	}
	if (!handshake(cToSSoc)){
		updateLock.unlock();
		return;
	}

	while (true){
		std::tuple<std::string, std::string> command = getCommand();
		if (command == std::tuple<std::string, std::string>("",""))
			continue;
		std::string action = std::get<0>(command);
		if (action.compare("end") != 0 && action.compare("update") != 0 && action.compare("delete") != 0)
			continue;
		sendMsg(cToSSoc, action);

		if (action.compare("update") == 0 || action.compare("delete") == 0){
			std::string data = std::get<1>(command);
			sendMsg(cToSSoc, data);
		}
		
		std::string feedback = recvMsg(cToSSoc);
		if (feedback.compare("goodbye") == 0){
			std::cout << "threadCtoS to close" << std::endl;
			closesocket(cToSSoc);
			updateLock.unlock();
			return;
		}
	}
	
}

std::string getUpdate(){
	dataLock.lock();
	if (updates.size() == 0){
		dataLock.unlock();
		return "";
	}
	std::string retElem = updates.front();
	updates.pop();
	dataLock.unlock();
	return retElem;
}

std::string getDelete(){
	dataLock.lock();
	if (deletes.size() == 0){
		dataLock.unlock();
		return "";
	}
	std::string retElem = deletes.front();
	deletes.pop();
	dataLock.unlock();
	return retElem;
}

std::tuple<std::string, std::string> getCommand(){
	dataLock.lock();
	if (commands.size() == 0){
		dataLock.unlock();
		return std::tuple<std::string, std::string>("", "");
	}
	std::tuple<std::string, std::string> retElem = commands.front();
	commands.pop();
	dataLock.unlock();
	return retElem;
}

void sendCommand(std::string action, std::string data){
	dataLock.lock();
	commands.push(std::tuple<std::string, std::string>(action, data));
	dataLock.unlock();
}


void threadStoC(float t){
	DWORD msInterval = t * 1000;
	SOCKET sToCSoc = setupClientSocket(host, port);

	setsockopt(sToCSoc, SOL_SOCKET, SO_RCVTIMEO, (char *)&msInterval, sizeof(DWORD));
	if (sToCSoc == INVALID_SOCKET){
		return;
	}
	if (!handshake(sToCSoc)){
		std::cout << "threadStoC finished" << std::endl;
		return;
	}

	sendMsg(sToCSoc, "period");
	sendMsg(sToCSoc, std::to_string(t));

	while (true){
		Sleep(msInterval);
		if (updateLock.try_lock()){
			updateLock.unlock();
			std::cout << "threadCtoS to end" << std::endl;
			sendMsg(sToCSoc, "end");
			recvMsg(sToCSoc);
			closesocket(sToCSoc);
			break;
		}
		std::string up;
		std::string del;
		try{
			up = recvMsg(sToCSoc);
			del = recvMsg(sToCSoc);
		}
		catch (const std::runtime_error& e) {
			continue;
		}
		
		dataLock.lock();
		if (up.length() > 0){
			updates.push(up);
		}
		if (del.length() > 0){
			deletes.push(del);
		}
		dataLock.unlock();
	}
	std::cout << "threadStoC finished" << std::endl;
}

bool handshake(SOCKET soc){
	try{
		sendMsg(soc, std::to_string(id));
		std::string errorCode = recvMsg(soc);
		if (errorCode.compare("ok") != 0){
			std::cout << errorCode << std::endl;
			closesocket(soc);
			std::cout << "Error, please close program" << std::endl;
			return false;
		}
		return true;
	}
	catch (std::exception& e){
		std::cout << "Error in handshake, please close program" << std::endl;
		return false;
	}

}

void begin(std::string action, float t){
	if (action.compare("end") == 0){
		std::cout << "Goodbye" << std::endl;
		return;
	}

	SOCKET soc = setupClientSocket(host, port);
	if (soc == INVALID_SOCKET){
		return;
	}

	if (action.compare("new") == 0){
		sendMsg(soc, action);
		id = std::stol(recvMsg(soc));
	}
	else{
		sendMsg(soc, action);
	}

	std::string errorCode = recvMsg(soc);
	if (errorCode.compare("ok") != 0){
		std::cout << errorCode << std::endl;
		closesocket(soc);
		std::cout << "Please exit the program now" << std::endl;
		return;
	}

	if (action.compare("new") != 0){
		id = std::stol(action);
	}
	std::cout << "You are id " << id << std::endl;
	std::cout << "Use that id to login in the future" << std::endl;

	sendMsg(soc, "end_register");
	recvMsg(soc);
	closesocket(soc);
}