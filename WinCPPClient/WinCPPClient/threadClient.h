/*
 * Function to be on a thread to continuously send the update/delete action along with the data to be update/delete from the commands queue.
 * On the end command, the socket get closed and the function is returned.
 */
void threadCtoS();

/*
 * Helper function to pop out and return an element from the front of updates queue, which stores updates received from the server.
 * If the updates queue is empty, the function return empty string.
 */
std::string getUpdate();

/*
 * Helper function to pop out and return an element from the front of deletes queue, which stores deletes received from the server.
 * If the deletes queue is empty, the function return empty string.
 */
std::string getDelete();

/*
 * Helper function to pop out and return an element from the front of commands queue, which stores the commands as tuples of action and data.
 * If the commands queue is empty, the function return ("", "").
 */
std::tuple<std::string, std::string> getCommand();

/*
 * Helper function to push a command (with the specified action and data) to the commands queue.
 */
void sendCommand(std::string action, std::string data);

/*
 * Function to be on a thread to periodically receive update/delete data from the server every t second(s) and push them into updates and deletes queues.
 */
void threadStoC(float t);

/*
 * Helper function to "sign in" to the server, using id
 * In the successful case, the function return true; otherwise, return false.
 */
bool handshake(SOCKET soc);

/*
 * Function to register the client by setting up the id
 * The parameter action could be 'new' to ask the server for a new id, the existing id that you already registered, or 'end' to exit.
 * The parameter t is the time interval in second(s) that the client would receive the update/delete data from the server.
 */
void begin(std::string action, float t);
