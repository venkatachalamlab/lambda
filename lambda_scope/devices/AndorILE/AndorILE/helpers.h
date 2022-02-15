#pragma once

#include <string>
#include <algorithm>
#include <iterator>

#include "macros.h"

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

	//DEBUG("Sending message: " << string);

	zmq::message_t message(string.size());
	memcpy(message.data(), string.data(), string.size());

	zmq::detail::send_result_t result = socket.send(message,
		zmq::send_flags::none);
}
