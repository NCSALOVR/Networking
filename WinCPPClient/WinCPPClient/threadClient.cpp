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
		//if there's nothing in the commands queue, continue on the loop
		std::tuple<std::string, std::string> command = getCommand();
		if (command == std::tuple<std::string, std::string>("",""))
			continue;

		//send the valid command action (i.e., end, update, or delete)
		std::string action = std::get<0>(command);
		if (action.compare("end") != 0 && action.compare("update") != 0 && action.compare("delete") != 0)
			continue;
		sendMsg(cToSSoc, action);

		//send the data if the action is update or delete
		if (action.compare("update") == 0 || action.compare("delete") == 0){
			std::string data = std::get<1>(command);
			sendMsg(cToSSoc, data);
		}
		
		//close the socket and end the function if the action is end
		if (action.compare("end") == 0){
			std::string feedback = recvMsg(cToSSoc);
			if (feedback.compare("goodbye") == 0){
				closesocket(cToSSoc);
				updateLock.unlock();
				return;
			}
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

	//set timeout for recv() to be the same as period interval t
	setsockopt(sToCSoc, SOL_SOCKET, SO_RCVTIMEO, (char *)&msInterval, sizeof(DWORD));

	if (sToCSoc == INVALID_SOCKET){
		return;
	}
	if (!handshake(sToCSoc)){
		std::cout << "threadStoC finished" << std::endl;
		return;
	}

	//send period action to the server
	sendMsg(sToCSoc, "period");
	sendMsg(sToCSoc, std::to_string(t));

	while (true){
		Sleep(msInterval);

		/*
		The function can only acquire the update lock when the end command has been sent to the server in the threadCtoS()
		and the thread to send update/delete to the server is about to terminate. 
		So upon acquiring the updatelock (i.e., updateLock.try_lock() is true), close the socket and exit from the function to terminate the thread.
		*/
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
		//this is in the case of timeout (i.e., nothing has been sent from the server)
		catch (const std::runtime_error& e) {
			continue;
		}
		
		//push the received nonempty update and delete to the queues.
		dataLock.lock();
		if (up.compare("{}") != 0){
			updates.push(up);
		}
		if (del.compare("{}") != 0){
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
		//in the case that parameter action is the existing id
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