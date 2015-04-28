#include <cstdint>

/*
 * Helper function to create window socket and initiate a TCP connection to the specified host and port.
 * It return a SOCKET (with the value of INVALID_SOCKET in the case of error).
 */
SOCKET setupClientSocket(const char * host, const char * port);

/*
 * Helper function to send a msg on the socket sockfd.
 */
void sendMsg(SOCKET sockfd, std::string msg);

/*
 * Helper function to receive a msg on the socket sockfd and return it.
 * On error (most likely from timeout), the function throw std::runtime_error exception 
 */
std::string recvMsg(SOCKET sockfd);

/*
 * Helper function to receive the specified number of bytes (i.e., num_bytes) on the socket sockfd.
 */
std::string recvNumBytes(SOCKET sockfd, uint32_t num_bytes);