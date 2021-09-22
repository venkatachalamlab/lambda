// AndorZylaCamera.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
// Start a single Andor Zyla camera, and connect it to a subscriber
// for commands, a publisher for status and state updates, and a
// publisher to broadcast image data.
//
//
// Configuration:
// ZMQ and docopt should be installed using vcpkg (both windows-x64)
// Change the 'Solution platform' to x64 (It is x86 by default)
// Chnage the 'Solution configuration' to Debug.
// Project properties:
//      make sure "Configuration" (top - left) is set to "Debug" for the next steps.
//      Configuration Properties -> Windows SDK Version -> 10.0.17763.0
//      Configuration Properties -> Platform Toolset -> Visual Studio 2017 (v141)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(ANDOR_SDK)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(CXXOPTS)
//      Configuration Properties -> C/C++ -> Language -> C++ Language Standard = ISO C++17 Standard (/std:c++17)
//      Configuration Properties -> Linker -> General -> Additional Library Directories = $(ANDOR_SDK)
//      Configuration Properties -> Linker -> Input -> Additional Dependencies += atcorem.lib; atutilitym.lib;
//      Change "Configuration" (top-left) to "Debug" for the next steps.
//      Configuration Properties -> Build Events -> Post-Build Event -> Command Line =
//                                  if not exist "$(LAMBDA)\lambda_scope\camera\bin\debug\" mkdir "$$(LAMBDA)\lambda_scope\camera\bin\debug\"
//                                  copy "$(OutDir)*.exe" "$(LAMBDA)\lambda_scope\camera\bin\debug"
//                                  copy "$(OutDir)*.dll" "$(LAMBDA)\lambda_scope\camera\bin\debug"
// Ensure $(LAMBDA)\lambda_scope\camera\bin\debug is added to 'Path' system variable
// Ensure 'VENKATACHALAMLAB' and 'ANDOR_SDK' are in your system path (set them as environment variables).

#include "pch.h"
#include <iostream>
#include <chrono>

#include "cxxopts.hpp"
#include "zmq.hpp"

#include "macros.h"
#include "helpers.h"
#include "Zyla.h"


std::string update_status(std::string name, int stack_size, bool running, bool device_status)
{
    std::ostringstream s;
    s << "{\"" << name << "\": {\"stack_size\": "
        << stack_size << ", \"running_status\": " << running << ", \"device_status\": " << device_status << "}}";

    return s.str();
}


cxxopts::ParseResult parse(int argc, char* argv[])
{
    try
    {
        cxxopts::Options options(argv[0], "- Command line options for AndorZylaCamera.");

        options.positional_help("[optional args]");
        options.show_positional_help();

        options.add_options()
            ("help", "Print Help.")
            ("commands", "Connection for inbound commands.", cxxopts::value<std::string>()->default_value("localhost:5001"))
            ("status", "Connection for outbound status messages.", cxxopts::value<std::string>()->default_value("localhost:5000"))
            ("data", "Bound port used to publish image data.", cxxopts::value<std::string>()->default_value("*:5003"))
            ("name", "Name of device for filtering commands.", cxxopts::value<std::string>()->default_value("ZylaCamera"))
            ("serial_number", "Determines which camera is used.", cxxopts::value<std::string>()->default_value("VSC-08793"))
            ("trigger_mode", "Takes integers 1 or 2, and Sets the trigger mode to 'Internal' or 'ExternalExposure'", cxxopts::value<int>()->default_value("1"))
            ("stack_size", "Number of steps that the piezo takes in each cycle.", cxxopts::value<int>()->default_value("25"))
			("y_shape", "Height of the image.", cxxopts::value<int>()->default_value("512"))
			("x_shape", "Width of the image.", cxxopts::value<int>()->default_value("512"))
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



int main(int argc, char *argv[])
{

    auto result = parse(argc, argv);

    zmq::context_t zmq_context(1);

    // Create a socket to get commands.

    zmq::socket_t commands(zmq_context, ZMQ_SUB);

    int stack_size = result["stack_size"].as<int>();
	int y_shape = result["y_shape"].as<int>();
	int x_shape = result["x_shape"].as<int>();
    
    std::string inbound = "tcp://" + result["commands"].as<std::string>();
    DEBUG("Subscribing to commands on " << inbound);
    commands.connect(inbound);

    const char* name = result["name"].as<std::string>().c_str();
    DEBUG("Subscribing to commands beginning with " << name);
    commands.setsockopt(ZMQ_SUBSCRIBE, name, strlen(name));

    // Create a socket to publish state/status.
    zmq::socket_t updates(zmq_context, ZMQ_PUB);

    std::string outbound = "tcp://" + result["status"].as<std::string>();
    DEBUG("Publishing updates on " << outbound);
    updates.connect(outbound);

    // Create a socket to publish image data.
    zmq::socket_t data_socket(zmq_context, ZMQ_PUB);

    std::string image_port = "tcp://" + result["data"].as<std::string>();
    DEBUG("Publishing images on " << image_port);
    data_socket.bind(image_port);

    std::string serial_number = result["serial_number"].as<std::string>();
    int trigger_mode = result["trigger_mode"].as<int>();


    std::optional<std::string> cmd_msg;
    std::string cmd;
    const int name_length = strlen(name);

    // Set up camera.
    Zyla camera(serial_number);

    std::string device_name(name);
    camera.set_binning(4);
    camera.set_AOI_height(y_shape);
    camera.set_AOI_width(x_shape);
    camera.set_VerticallyCenterAOI(true);
    camera.set_trigger_mode(trigger_mode);
    if (trigger_mode == 1)
        stack_size = 1;
    camera.prepare();

    bool camera_running = false;
    bool app_running = true;

    std::string status = update_status(device_name, stack_size, camera_running, app_running);
    

    while (app_running) {

        if (camera_running)
            cmd_msg = s_recv_dontwait(commands);
        else // Block for a command.
            cmd_msg = s_recv(commands);


        if (cmd_msg)
        {
            cmd = (*cmd_msg).substr(name_length + 1);

            if (cmd.substr(0,16).compare("set_trigger_mode") == 0)
            {
                trigger_mode = std::stoi(cmd.substr(17));
                camera.set_trigger_mode(trigger_mode);

                if (trigger_mode == 1)
                {
                    stack_size = 1;
                }
                status = update_status(device_name, stack_size, camera_running, app_running);
                s_send(updates, "hub " + status);
                s_send(updates, "logger " + status);
            }
            else if (cmd.substr(0, 14).compare("set_stack_size") == 0)
            {
                stack_size = std::stoi(cmd.substr(15));

                if (trigger_mode == 1)
                {
                    stack_size = 1;
                }
                status = update_status(device_name, stack_size, camera_running, app_running);
                s_send(updates, "hub " + status);
                s_send(updates, "logger " + status);
            }
			// start new
			else if (cmd.substr(0, 9).compare("set_shape") == 0)
			{
				std::string params = cmd.substr(10);
				int y, x, pos;
				
				pos = params.find(" ");
				stack_size = std::stoi(params.substr(0, pos));
				params.erase(0, pos + 1);
				pos = params.find(" ");
				y = std::stoi(params.substr(0, pos));
				params.erase(0, pos + 1);
				x = std::stoi(params);

				if (trigger_mode == 1)
				{
					stack_size = 1;
				}

				camera.finish_continuous();

				camera.set_AOI_height(y);
				camera.set_AOI_width(x);
				camera.set_VerticallyCenterAOI(true);

				camera.prepare();

				status = update_status(device_name, stack_size, camera_running, app_running);
				s_send(updates, "hub " + status);
				s_send(updates, "logger " + status);
			}
			// end new
            else if (cmd.compare("start") == 0)
            {
                if(!camera_running)
                {
					camera.start_continuous();
                    camera_running = camera.get_camera_acquiring();
                    status = update_status(device_name, stack_size, camera_running, app_running);
                    s_send(updates, "hub " + status);
                    s_send(updates, "logger " + status);
                }
            } 
            else if (cmd.compare("stop") == 0)
            {
                if (camera_running)
                {
					camera.pause_continuous();
                    camera_running = camera.get_camera_acquiring();
                    status = update_status(device_name, stack_size, camera_running, app_running);
                    s_send(updates, "hub " + status);
                    s_send(updates, "logger " + status);
                }
            }
            else if (cmd.compare("publish_status") == 0 )
            {
                status = update_status(device_name, stack_size, camera_running, app_running);
                s_send(updates, "hub " + status);
                s_send(updates, "logger " + status);
            }
            else if (cmd.compare("shutdown") == 0)
            {
                camera.finish_continuous();
                camera_running = camera.get_camera_acquiring();
                app_running = false;
                status = update_status(device_name, stack_size, camera_running, app_running);
                s_send(updates, "hub " + status);
                s_send(updates, "logger " + status);
            }
            
        }
        
        else if (camera_running)
        {
            unsigned char *data = (unsigned char*) malloc(camera.image_size * stack_size);

            for (int i=0; i < stack_size; i++)
            {
				camera.get_image(data + i * camera.image_size);
            }

            zmq::message_t msg(data, camera.image_size * stack_size, *my_free);

            data_socket.send(msg, zmq::send_flags::none);
        }

    }
    return 0;
}
