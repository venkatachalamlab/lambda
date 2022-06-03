// AndorILE.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
// Starts communication with Andor ILE device, and connects it to a subscriber
// for commands, a publishers for status updates.
//
//
// Configuration:
// ZMQ should be installed using vcpkg (both windows-x64)
// Change the 'Solution platform' to x64 (It is x86 by default)
// Chnage the 'Solution configuration' to Debug.
// Project properties:
//      Change "Configuration" (top-left) to "Debug" for the next steps.
//      Configuration Properties -> Windows SDK Version -> 10.0.17763.0
//      Configuration Properties -> Platform Toolset -> Visual Studio 2017 (v141)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(ANDOR_ALC_SDK)\include
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(CXXOPTS)
//      Configuration Properties -> C/C++ -> Language -> C++ Language Standard = ISO C++17 Standard (/std:c++17)
//      Configuration Properties -> Linker -> General -> Additional Library Directories = $(ANDOR_ALC_SDK)\Libraries
//      Configuration Properties -> Buld Events -> Post-Build Event -> Command Line= 
//                                  if not exist "$(LAMBDA_CPP_BIN)" mkdir "$$(LAMBDA_CPP_BIN)"
//                                  copy "$(OutDir)*.exe" "$(LAMBDA_CPP_BIN)"
//                                  copy "$(OutDir)*.dll" "$(LAMBDA_CPP_BIN)"
//
// Ensure $(LAMBDA_CPP_BIN) is added to 'Path' system variable
// Ensure 'ANDOR_ALC_SDK' are in your system path (set them as environment variables).


#include <stdio.h>
#include <math.h>
#include <tchar.h>
#include <iterator>
#include <iostream>

#include "cxxopts.hpp"
#include "zmq.hpp"

#include "ILE_REVModuleHandler.h"
#include "ALC_REV.h"
#include "macros.h"
#include "helpers.h"

std::string update_status(std::string name, int low_power_status, bool device_status)
{
	std::ostringstream s;
	s << "{\"" << name <<
		"\": {\"low_power\": " << low_power_status <<
		", \"device\": " << device_status << "}}";
	return s.str();
}


void print_power_management_status(IALC_REV_ILEPowerManagement  * ALC_REVPowerManagement, IALC_REV_Laser2 *ALC_REVLaser2)
{
	bool is_low_power_present;
	bool is_low_power_enabled;
	bool low_power_state;
	int low_power_port;
	bool is_coherence_mode_present;
	bool is_coherence_mode_active;
	TLaserState laser_state;
	ALC_REVPowerManagement->IsLowPowerPresent(&is_low_power_present);
	ALC_REVPowerManagement->IsLowPowerEnabled(&is_low_power_enabled);
	ALC_REVPowerManagement->GetLowPowerState(&low_power_state);
	ALC_REVPowerManagement->GetLowPowerPort(&low_power_port);
	ALC_REVPowerManagement->IsCoherenceModePresent(&is_coherence_mode_present);
	ALC_REVPowerManagement->IsCoherenceModeActive(&is_coherence_mode_active);

	ALC_REVLaser2->GetLaserState(1, &laser_state);

	std::cout << "************************" << std::endl;
	std::cout << "ALC_REVPowerManagement->IsLowPowerPresent(&is_low_power_present);" << std::endl;
	std::cout << "is_low_power_present=" << is_low_power_present << std::endl << std::endl;

	std::cout << "ALC_REVPowerManagement->IsLowPowerEnabled(&is_low_power_enabled);" << std::endl;
	std::cout << "is_low_power_enabled=" << is_low_power_enabled << std::endl << std::endl;

	std::cout << "ALC_REVPowerManagement->GetLowPowerState(&low_power_state);" << std::endl;
	std::cout << "low_power_state=" << low_power_state << std::endl << std::endl;

	std::cout << "ALC_REVPowerManagement->GetLowPowerPort(&low_power_port);" << std::endl;
	std::cout << "low_power_port=" << low_power_port << std::endl << std::endl;


	std::cout << "ALC_REVPowerManagement->IsCoherenceModePresent(&is_coherence_mode_present);" << std::endl;
	std::cout << "is_coherence_mode_present=" << is_coherence_mode_present << std::endl << std::endl;


	std::cout << "ALC_REVPowerManagement->IsCoherenceModeActive(&is_coherence_mode_active);" << std::endl;
	std::cout << "is_coherence_mode_active=" << is_coherence_mode_active << std::endl << std::endl;

	std::cout << "ALC_REVLaser2->GetLaserState(1, &laser_state);" << std::endl;
	std::cout << "laser_state=" << laser_state << std::endl << std::endl;
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
			("name", "Name of device.", cxxopts::value<std::string>()->default_value("AndorILE"))
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

	zmq::socket_t commands(zmq_context, ZMQ_SUB);


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



	TILE_REV2ModuleHandler ILE_REV2ModuleHandler;

	IALC_REVObject3 *ALC_REVObject3 = ILE_REV2ModuleHandler.GetALC_REVObject3();
	if (ALC_REVObject3 == 0)
		DEBUG("GetALC_REVObject failed\n");

	IALC_REV_Laser2 *ALC_REVLaser2 = ALC_REVObject3->GetLaserInterface2();
	if (ALC_REVLaser2 == 0)
		DEBUG("GetLaserInterface2 failed\n");

	IALC_REV_ILEPowerManagement  * ALC_REVPowerManagement = ILE_REV2ModuleHandler.GetALC_REVPowerManagement();
	if (ALC_REVPowerManagement == 0)
		DEBUG("GetALC_REVPowerManagement failed\n");

	int NumberOfLasers = ALC_REVLaser2->Initialize();
	//print_power_management_status(ALC_REVPowerManagement, ALC_REVLaser2);
	for (int LaserIndex = 1; LaserIndex <= NumberOfLasers; LaserIndex++)
	{
		ALC_REVLaser2->Enable(LaserIndex);
	}

	const int name_length = strlen(name);
	std::string device_name(name);
	std::optional<std::string> cmd_msg;
	std::string cmd;

	bool low_power_status = false;
	bool app_running = true;

	ALC_REVPowerManagement->SetCoherenceMode(false);
	ALC_REVPowerManagement->SetLowPowerState(low_power_status);

	ALC_REVPowerManagement->GetLowPowerState(&low_power_status);

	std::string status = update_status(device_name, low_power_status, app_running);
	s_send(updates, "hub " + status);
	s_send(updates, "logger " + status);

	//print_power_management_status(ALC_REVPowerManagement, ALC_REVLaser2);
	while (app_running)
	{
		cmd_msg = s_recv(commands);
		if (cmd_msg)
		{
			cmd = (*cmd_msg).substr(name_length + 1);

			if (cmd.substr(0, 13).compare("set_nd_filter") == 0)
			{
				int low_power_request = std::stoi(cmd.substr(14));
				ALC_REVPowerManagement->SetLowPowerState((bool)low_power_request);
				ALC_REVPowerManagement->SetCoherenceMode(false);
				ALC_REVPowerManagement->GetLowPowerState(&low_power_status);

				status = update_status(device_name, low_power_status, app_running);
				s_send(updates, "hub " + status);
				s_send(updates, "logger " + status);
				//print_power_management_status(ALC_REVPowerManagement, ALC_REVLaser2);
			}

			else if (cmd.substr(0, 8).compare("shutdown") == 0)
			{
				ALC_REVPowerManagement->SetCoherenceMode(false);
				ALC_REVPowerManagement->SetLowPowerState(false);
				for (int LaserIndex = 1; LaserIndex <= NumberOfLasers; LaserIndex++)
				{
					ALC_REVLaser2->SetLas_I(LaserIndex, 0.0, false);
					ALC_REVLaser2->Disable(LaserIndex);
				}
				app_running = false;

				status = update_status(device_name, low_power_status, app_running);
				s_send(updates, "hub " + status);
				s_send(updates, "logger " + status);
				//print_power_management_status(ALC_REVPowerManagement, ALC_REVLaser2);
			}
		}
	}
	return 0;
}

