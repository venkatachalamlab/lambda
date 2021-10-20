// Configuration:
// ZMQ and docopt should be installed using vcpkg (both windows-x64)
// Project properties:
//      Configuration Properties -> Windows SDK Version -> 10.0.17763.0
//      Configuration Properties -> Platform Toolset -> Visual Studio 2017 (v141)
//      Configuration Properties -> C/C++ -> General -> Additional Include Directories = $(CXXOPTS)
//      Configuration Properties -> C/C++ -> Language -> C++ Language Standard = ISO C++17 Standard (/std:c++17)
//      Configuration Properties -> Linker -> Input -> Additional Dependencies = Xinput9_1_0.lib
//      Change "Configuration" (top-left) to "Debug" for the next steps.
//      Configuration Properties -> Buld Events -> Post-Build Event -> Command Line =
//                                  if not exist "$(LAMBDA_CPP_BIN)" mkdir "$(LAMBDA_CPP_BIN)"
//									copy  "$(OutDir)*.exe" "$(LAMBDA_CPP_BIN)"
//									copy  "$(OutDir)*.dll" "$(LAMBDA_CPP_BIN)"
//     
//    
// Ensure 'CXXOPTS' and 'LAMBDA_CPP_BIN' are in your system path (set them as environment variables).



#include "pch.h"
#include <iostream>
#include <WinSock2.h>
#include <Windows.h>
#include <Xinput.h>

#include "zmq.hpp"
#include "cxxopts.hpp"

cxxopts::ParseResult parse(int argc, char* argv[])
{
    try
    {
        cxxopts::Options options(argv[0], "- Command line options for XInputToZMQPub.");

        options.positional_help("[optional args]");
        options.show_positional_help();

        options.add_options()
            ("help", "Print Help.")
            ("outbound", "Publisher host and port.", cxxopts::value<std::string>()->default_value("*:5557"))
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


    zmq::context_t context(1);

    zmq::socket_t socket(context, ZMQ_PUB);
    std::string address = "tcp://" + result["outbound"].as<std::string>();
    socket.bind(address);

    // Keep only the last message.
    socket.setsockopt(ZMQ_CONFLATE, 1);

    // Prepare controller state.
    DWORD dwResult;

    XINPUT_STATE state;
    ZeroMemory(&state, sizeof(XINPUT_STATE));

    DWORD current_packet_number = 0;

    while (true)
    {

        dwResult = XInputGetState(0, &state);
        if (dwResult == ERROR_SUCCESS
            && state.dwPacketNumber != current_packet_number)
        {
            current_packet_number = state.dwPacketNumber;
            zmq::message_t reply(sizeof(XINPUT_GAMEPAD));
            memcpy(reply.data(), &state.Gamepad, sizeof(XINPUT_GAMEPAD));
            socket.send(reply, zmq::send_flags::none);

            //std::cout << current_packet_number << std::endl;

        }

        Sleep(16);

    }

    return 0;
}



