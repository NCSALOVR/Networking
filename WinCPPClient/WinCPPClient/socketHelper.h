#include <cstdint>

SOCKET setupClientSocket(const char * host, const char * port);
void sendMsg(SOCKET sockfd, std::string msg);
std::string recvMsg(SOCKET sockfd);
std::string recvNumBytes(SOCKET sockfd, uint32_t num_bytes);