// Configuration:
// ZMQ and docopt should be installed using vcpkg (both windows-x64)
// Project properties:
//      Configuration Properties -> Windows SDK Version -> 10.0.17763.0
//      Configuration Properties -> Platform Toolset -> Visual Studio 2017 (v141)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(CXXOPTS)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(SPINNAKER_SDK)\include
//      Configuration Properties -> C/C++ -> Language -> C++ Language Standard = ISO C++17 Standard (/std:c++17)
//      Configuration Properties -> Linker -> General -> Additional Library Directories = $(SPINNAKER_SDK)\lib64\vs2015
//      Configuration Properties -> Linker -> Input -> Additional Dependencies = Spinnakerd_v140.lib
//      Change "Configuration" (top-left) to "Debug" for the next steps.
//      Configuration Properties -> Buld Events -> Post-Build Event -> Command Line =
//                                  if not exist "$(LAMBDA_CPP_BIN)" mkdir "$(LAMBDA_CPP_BIN)"
//									copy  "$(OutDir)*.exe" "$(LAMBDA_CPP_BIN)"
//									copy  "$(OutDir)*.dll" "$(LAMBDA_CPP_BIN)"
//   
// Ensure 'LAMBDA_CPP_BIN', 'CXXOPTS' and 'SPINNAKER_SDK' are in your system path (set them as environment variables). 

#include "pch.h"
#include <iostream>
#include <string>
#include <vector>
#include <iterator>
#include <sstream>
#include <optional>

#include "zmq.hpp"
#include "cxxopts.hpp"

#include "SpinnakerCamera.h"
#include "macros.h"
#include "helpers.h"

cxxopts::ParseResult parse(int argc, char* argv[])
{
	try
	{
		cxxopts::Options options(argv[0], "- Command line options for FlirCamera.");

		options.positional_help("[optional args]");
		options.show_positional_help();

		options.add_options()
			("help", "Print Help.")
			("serial_number", "Camera serial number.", cxxopts::value<int>()->default_value("17549024"))
			("commands", "Command subscriber.", cxxopts::value<std::string>()->default_value("localhost:5001"))
			("name", "Device name.", cxxopts::value<std::string>()->default_value("FlirCamera"))
			("status", "Status Publisher.", cxxopts::value<std::string>()->default_value("localhost:5000"))
			("data", "Data publisher.", cxxopts::value<std::string>()->default_value("*:6002"))
			("binsize", "Binning size.", cxxopts::value<int>()->default_value("2"))
			("width", "Image width.", cxxopts::value<int>()->default_value("512"))
			("height", "Image height.", cxxopts::value<int>()->default_value("512"))
			("exposure_time", "Camera exposure time in micro second.", cxxopts::value<double>()->default_value("10000.0"))
			;

		auto result = options.parse(argc, argv);

		if (result.count("help"))
		{
			std::cout << options.help({}) << std::endl;
			exit(0);
		}

		return result;
	}
	catch (const cxxopts::OptionException& e)
	{
		std::cout << "error parsing options: " << e.what() << ". use --help to display options." << std::endl;
		exit(1);
	}
}

void my_free(void *data, void *hint)
{
	free(data);
}

int main(int argc, char *argv[])
{

	auto result = parse(argc, argv);

	int serial_number = result["serial_number"].as<int>();
	int binsize = result["binsize"].as<int>();
	int width = result["width"].as<int>();
	int height = result["height"].as<int>();
	double exposure_time = result["exposure_time"].as<double>();
	std::string name = result["name"].as<std::string>();
	std::string commands = result["commands"].as<std::string>();
	std::string status = result["status"].as<std::string>();
	std::string data = result["data"].as<std::string>();

	zmq::context_t context(1);

	zmq::socket_t subscriber(context, ZMQ_SUB);
	std::string subscriber_address = "tcp://";
	subscriber_address.append(commands);
	subscriber.connect(subscriber_address);
	subscriber.setsockopt(ZMQ_SUBSCRIBE, name.c_str(), name.length());

	zmq::socket_t publisher(context, ZMQ_PUB);
	std::string publisher_address = "tcp://";
	publisher_address.append(status);
	publisher.connect(publisher_address);

	zmq::socket_t image_publisher(context, ZMQ_PUB);
	std::string image_publisher_address = "tcp://";
	image_publisher_address.append(data);
	image_publisher.bind(image_publisher_address);

	std::optional<std::string> cmd_msg;
	std::string cmd;
	const int name_length = name.length();

	SpinnakerCamera camera = SpinnakerCamera(serial_number);

	camera.HorizontalBinSize = binsize;
	camera.VerticalBinSize = binsize;
	camera.Height = height;
	camera.Width = width;

	camera.set_binning();
	camera.set_width();
	camera.set_height();
	camera.set_Offset();

	camera.set_exposuretime_and_framerate(exposure_time, (double)((int)(1000000 / (1.02 * exposure_time))));
	std::cout << name << ": Initialized." << std::endl;


	bool camera_running = false;
	bool first_time_in_loop = true;

	while (true)
	{
		if (first_time_in_loop)
		{
			first_time_in_loop = false;
			camera.begin_acquisition();
			camera_running = true;
		}

		if (camera_running)
			cmd_msg = s_recv_dontwait(subscriber);
		else // Block for a command.
			cmd_msg = s_recv(subscriber);


		if (cmd_msg)
		{
			cmd = (*cmd_msg).substr(name_length + 1);

			if (cmd.compare("shutdown") == 0)
			{
				if (camera_running)
				{
					camera.end_acquisition();
					camera_running = false;
					DEBUG(name << ": Stopped.");
				}
				DEBUG(name << ": Shutting down.");
				break;
			}

			else if (cmd.compare("start") == 0)
			{
				if (!camera_running)
				{
					camera.begin_acquisition();
					camera_running = true;
					DEBUG(name << ": Running.");
				}
			}

			else if (cmd.compare("stop") == 0)
			{
				if (camera_running)
				{
					camera.end_acquisition();
					camera_running = false;
					DEBUG(name << ": stopped.");
				}
			}

			else if (cmd.substr(0, 12).compare("set_exposure") == 0)
			{
				if (camera_running)
				{
					camera.end_acquisition();
					camera_running = false;
				}
				cmd.erase(0, 13);
				std::cout << cmd << std::endl;
				std::string space_delimiter = " ";
				size_t delimeter_pos = cmd.find(space_delimiter);
				double exposure = stod(cmd.substr(0, delimeter_pos));
				cmd.erase(0, delimeter_pos + space_delimiter.length());
				double rate = stod(cmd);
				camera.set_exposuretime_and_framerate(exposure, rate);
			}

			else if (cmd.substr(0, 10).compare("set_height") == 0)
			{
				if (camera_running)
				{
					camera.end_acquisition();
					camera_running = false;
				}
				camera.Height = std::stoi(cmd.substr(11));
				camera.set_binning();
				camera.set_width();
				camera.set_height();
				camera.set_Offset();
			}

			else if (cmd.substr(0, 9).compare("set_width") == 0)
			{
				if (camera_running)
				{
					camera.end_acquisition();
					camera_running = false;
				}
				camera.Width = std::stoi(cmd.substr(10));
				camera.set_binning();
				camera.set_width();
				camera.set_height();
				camera.set_Offset();
			}
		}

		else if (camera_running)
		{
			char *data = (char*)malloc(camera.get_image_size_bytes());
			camera.get_image(reinterpret_cast<void*>(data));
			zmq::message_t msg(data, camera.get_image_size_bytes(), *my_free);
			image_publisher.send(msg, zmq::send_flags::none);
		}
	}

	camera.deinitialize_camera();

	return 0;
}

