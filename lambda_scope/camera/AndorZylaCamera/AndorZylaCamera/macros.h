#pragma once

// Comment to hide debug output.
//#define DEBUG_ON

#ifdef DEBUG_ON
#define DEBUG(x) std::cout << x << std::endl
#else 
#define DEBUG(x)
#endif

#define PRINT(x) std::cout << x << std::endl
#define WARNING(x) std::cout << "Warning: " << x << std::endl
#define ERROR(x) std::cout << "Error: " << x << std::endl