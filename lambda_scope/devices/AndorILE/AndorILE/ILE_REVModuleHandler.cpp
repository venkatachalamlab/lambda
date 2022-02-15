#include <windows.h>
#include "ILE_REVModuleHandler.h"

#include "ALC_REV.h"
#include <iostream>

#include "macros.h"

//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
TILE_REV2ModuleHandler::TILE_REV2ModuleHandler(void)
	: Create_ILE_Detection_(NULL),
	Delete_ILE_Detection_(NULL),
	ILE_Detection_(NULL),
	Create_ILE_REV3_(NULL),
	Delete_ILE_REV3_(NULL),
	ALC_REVObject3_(NULL),
	Get_ILE_PowerManagementInterface_(NULL)
{
	// throw to prevent the class from being created 
	// if the library not found
	// or fails to get the function pointer 

#if defined _M_X64 
	hDLL_ = LoadLibraryA("AB_ALC_REV64.dll");
#else
	hDLL_ = LoadLibraryA("AB_ALC_REV.dll");
#endif
	if (hDLL_ == NULL)
	{
		std::cout << "LoadLibrary ALC_REV.dll Failed\n";
		throw "";
	}

	Create_ILE_Detection_ = (TCreate_ILE_Detection)GetProcAddress(hDLL_, "Create_ILE_Detection");

	if (Create_ILE_Detection_ == 0)
	{
		std::cout << "GetProcAddress Create_ILE_Detection failed\n";
		throw "";
	}

	Delete_ILE_Detection_ = (TDelete_ILE_Detection)GetProcAddress(hDLL_, "Delete_ILE_Detection");
	if (Delete_ILE_Detection_ == 0)
	{
		std::cout << "GetProcAddress Delete_ILE_Detection failed\n";
		throw "";
	}
	Create_ILE_Detection_(&ILE_Detection_);

	if (ILE_Detection_ == NULL)
		std::cout << "Create_ILE_Detection failed\n";


	Create_ILE_REV3_ = (TCreate_ILE_REV3)GetProcAddress(hDLL_, "Create_ILE_REV3");

	if (Create_ILE_REV3_ == 0)
	{
		std::cout << "GetProcAddress Create_ILE_REV3 failed\n";
		throw "";
	}

	Delete_ILE_REV3_ = (TDelete_ILE_REV3)GetProcAddress(hDLL_, "Delete_ILE_REV3");
	if (Delete_ILE_REV3_ == 0)
	{
		std::cout << "GetProcAddress Delete_ILE_REV3 failed\n";
		throw "";
	}


	Get_ILE_PowerManagementInterface_ = (TGetILEPowerManagementInterface)GetProcAddress(hDLL_, "GetILEPowerManagementInterface");
	if (Get_ILE_PowerManagementInterface_ == 0)
	{
		std::cout << "GetProcAddress GetILEPowerManagementInterface failed\n";
		throw "";
	}

#if 0
	//demo test
	//Create_ILE_REV_(&ALC_REVObject2_, "Demo");
	//JUST ADDED
	Create_ILE_REV_(&ALC_REVObject3_, "Demo");


#else 
	//use detection to get name
	int NumDevs = ILE_Detection_->GetNumberOfDevices();
	if (NumDevs == 0)
	{
		std::cout << "ILE_Detection detected no devices\n";
		throw "";
	}

	char Name[64];
	ILE_Detection_->GetSerialNumber(0, &Name[0], 64);

	Create_ILE_REV3_(&ALC_REVObject3_, Name);
	ALC_REVPowerManagement_ = Get_ILE_PowerManagementInterface_(ALC_REVObject3_);
#endif

	if (ALC_REVObject3_ != NULL)
		std::cout << "Laser: Initialized\n";
	else
		std::cout << "Create_ILE_REV failed\n";
	if (ALC_REVPowerManagement_ != NULL)
		DEBUG("PowerManagement instance created");
	else
		DEBUG("PowerManagement instance failed");
}



//---------------------------------------------------------------------------
TILE_REV2ModuleHandler::~TILE_REV2ModuleHandler(void)
{
	try
	{

		if (ILE_Detection_ != 0)
		{
			if (Delete_ILE_Detection_(ILE_Detection_) != true)
				std::cout << "Delete_ILE_Detection failed\n";
			ALC_REVObject3_ = 0;
		}

		if (ALC_REVObject3_ != 0)
		{
			if (Delete_ILE_REV3_(ALC_REVObject3_) == true)
				std::cout << "Delete_ALC_REV successful\n";
			else
				std::cout << "Delete_ALC_REV failed\n";
			ALC_REVObject3_ = 0;
		}

		if (hDLL_ != 0)
			FreeLibrary(hDLL_);
		hDLL_ = 0;
	}
	catch (...)
	{
	}
}
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------