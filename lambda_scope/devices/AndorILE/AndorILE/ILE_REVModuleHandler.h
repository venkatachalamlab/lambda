#pragma once
#include <Windows.h>

class IALC_REVObject3;//fwrd
class IILE_Detection;//fwrd
class IALC_REV_ILEPowerManagement;//fwrd
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
// simple class using RAII to load and unload the ALC_REV Module 
// and create and intstance of the ALC_REVObject
//---------------------------------------------------------------------------
class TILE_REV2ModuleHandler
{
private:
	HMODULE hDLL_;

	typedef bool(__stdcall *TCreate_ILE_Detection)(IILE_Detection **ILE_Detection);
	typedef bool(__stdcall *TDelete_ILE_Detection)(IILE_Detection *ILE_Detection);
	TCreate_ILE_Detection Create_ILE_Detection_;
	TDelete_ILE_Detection Delete_ILE_Detection_;

	IILE_Detection *ILE_Detection_;

	typedef bool(__stdcall *TCreate_ILE_REV3)(IALC_REVObject3 **ALC_REVObject3, const char *UnitID);
	typedef bool(__stdcall *TDelete_ILE_REV3)(IALC_REVObject3 *ALC_REVObject3);
	TCreate_ILE_REV3 Create_ILE_REV3_;
	TDelete_ILE_REV3 Delete_ILE_REV3_;

	IALC_REVObject3 *ALC_REVObject3_;


	typedef IALC_REV_ILEPowerManagement*(__stdcall *TGetILEPowerManagementInterface)(IALC_REVObject3 *ALC_REVObject3);
	TGetILEPowerManagementInterface Get_ILE_PowerManagementInterface_;
	IALC_REV_ILEPowerManagement *ALC_REVPowerManagement_;


public:

	TILE_REV2ModuleHandler(void);
	~TILE_REV2ModuleHandler(void);
	IALC_REVObject3 *GetALC_REVObject3() { return ALC_REVObject3_; };
	IALC_REV_ILEPowerManagement *GetALC_REVPowerManagement() { return ALC_REVPowerManagement_; }
};
