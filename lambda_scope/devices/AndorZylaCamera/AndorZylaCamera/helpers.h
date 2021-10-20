#pragma once

#include <string>
#include <algorithm>
#include <iterator>

#include "macros.h"

//// From http://www.martinbroadhurst.com/how-to-split-a-string-in-c.html
//template <class Container>
//void split(const std::string& str, Container& cont,
//    char delim = ' ')
//{
//    std::size_t current, previous = 0;
//    current = str.find(delim);
//    while (current != std::string::npos) {
//        cont.push_back(str.substr(previous, current - previous));
//        previous = current + 1;
//        current = str.find(delim, previous);
//    }
//    cont.push_back(str.substr(previous, current - previous));
//}

#include "zmq.hpp"

//  Receive string from 0MQ socket, and block until one is available.
static std::optional<std::string> s_recv(zmq::socket_t & socket) {

	zmq::message_t message;
	socket.recv(message);
	return std::string(static_cast<char*>(message.data()), message.size());

}

//  Receive string from 0MQ socket, but return immediately if nothing is available.
static std::optional<std::string> s_recv_dontwait(zmq::socket_t & socket) {

	zmq::message_t message;
	zmq::detail::recv_result_t result = socket.recv(message, zmq::recv_flags::dontwait);
	if (result)
	{
		return std::string(static_cast<char*>(message.data()), message.size());
	}
	else
	{
		return std::nullopt; // also ok: return {}
	}
}

//  Convert string to 0MQ string and send to socket
static void s_send(zmq::socket_t & socket, const std::string & string) {


	zmq::message_t message(string.size());
	memcpy(message.data(), string.data(), string.size());

	zmq::detail::send_result_t result = socket.send(message,
		zmq::send_flags::none);
}

// 0MQ Free function for zero copy sending.
void my_free(void *data, void *hint)
{
	//  We've allocated the buffer using malloc and
	//  at this point we deallocate it using free.
	free(data);
}