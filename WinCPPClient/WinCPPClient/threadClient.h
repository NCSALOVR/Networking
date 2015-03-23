void threadCtoS();
std::string getUpdate();
std::string getDelete();
std::tuple<std::string, std::string> getCommand();
void sendCommand(std::string action, std::string data);
void threadStoC(float t);
bool handshake(SOCKET soc);
void begin(std::string action, float t);