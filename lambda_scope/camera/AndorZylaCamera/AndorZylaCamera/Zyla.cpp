// Copyright 2019
// Author: Vivek Venkatachalam (vivekv2@gmail.com), Mahdi Torkashvand

#include "pch.h"
#include <string>
#include <iostream>
#include <codecvt>
#include <locale>
#include <thread>

// Andor SDK3
#include "atcore.h"
#include "atutility.h"

// Our stuff
#include "macros.h"
#include "Zyla.h"


int Zyla::get_int_prop(const wchar_t* property)
{
    AT_64 value;
    int AT_error_code;
    AT_error_code = AT_GetInt(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return static_cast<int>(value);
}

void Zyla::set_int_prop(const wchar_t* property, const int & value)
{
    AT_64 value_AT = AT_64(value);
    int AT_error_code;
    AT_error_code = AT_SetInt(Hndl, property, value_AT);
    check_AT_error(AT_error_code);
}

int Zyla::get_int_max(const wchar_t* property)
{
    AT_64 value;
    int AT_error_code;
    AT_error_code = AT_GetIntMax(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return int(value);
}

int Zyla::get_int_min(const wchar_t* property)
{
    AT_64 value;
    int AT_error_code;
    AT_error_code = AT_GetIntMin(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return int(value);
}

double Zyla::get_float_prop(const wchar_t* property)
{
    double value;
    int AT_error_code;
    AT_error_code = AT_GetFloat(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return value;
}

void Zyla::set_float_prop(const wchar_t* property, const double & value)
{
    int AT_error_code;
    AT_error_code = AT_SetFloat(Hndl, property, value);
    check_AT_error(AT_error_code);
}

double Zyla::get_float_max(const wchar_t* property)
{
    double value;
    int AT_error_code;
    AT_error_code = AT_GetFloatMax(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return value;
}

double Zyla::get_float_min(const wchar_t* property)
{
    double value;
    int AT_error_code;
    AT_error_code = AT_GetFloatMin(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return value;
}


std::string Zyla::get_enum_prop(const wchar_t* property)
{

    int idx;
    int AT_error_code;
    AT_error_code = AT_GetEnumIndex(Hndl, property, &idx);
    check_AT_error(AT_error_code);

    wchar_t value_WC[128];
    AT_error_code = AT_GetEnumStringByIndex(Hndl, property, idx,
        value_WC, 128);
    check_AT_error(AT_error_code);

    return string_from_wchar(value_WC);
}

void Zyla::set_enum_prop(const wchar_t* property, const wchar_t* value)
{
    int AT_error_code = AT_SetEnumString(Hndl, property, value);
    check_AT_error(AT_error_code);
}

bool Zyla::get_bool_prop(const wchar_t* property)
{
    AT_BOOL value;
    int AT_error_code = AT_GetBool(Hndl, property, &value);
    check_AT_error(AT_error_code);
    return bool(value);
}

void Zyla::set_bool_prop(const wchar_t* property, const bool value)
{
    const AT_BOOL value_AT = AT_BOOL(value);
    int AT_error_code;
    AT_error_code = AT_SetBool(Hndl, property, value_AT);
    check_AT_error(AT_error_code);
}

std::string Zyla::get_string_prop(const wchar_t* property)
{
    AT_WC value[64];
    int AT_error_code = AT_GetString(Hndl, property, value, 64);
    check_AT_error(AT_error_code);

    std::string str = string_from_wchar(value);

    return str;
}

void Zyla::set_string_prop(const wchar_t* property, const wchar_t* value)
{
}

void Zyla::command(const wchar_t* property)
{
    AT_Command(Hndl, property);
}


void Zyla::check_AT_error(int AT_return_code)
{
    if (AT_return_code != AT_SUCCESS) {
        ERROR("Andor SDK error code: " << AT_return_code);
    }
}

// This currently doesn't reliably generate properties and values
// that are interpreted correctly by the Andor SDK. Send wide strings
// for now.
// Possible fix:
// // Convert an UTF8 string to a wide Unicode String
////std::wstring utf8_decode(const std::string &str)
////{
////    if (str.empty()) return std::wstring();
////    int size_needed = MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), NULL, 0);
////    std::wstring wstrTo(size_needed, 0);
////    MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), &wstrTo[0], size_needed);
////    return wstrTo;
////}
//const wchar_t * Zyla::wchar_from_string(std::string s)
//{
//    std::wstring ws = std::wstring_convert<
//        std::codecvt_utf8<wchar_t>>().from_bytes(s);
//    return ws.c_str();;
//}

const std::string Zyla::string_from_wchar(const wchar_t* wc)
{
    size_t cbMultiByte;
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wc, wcslen(wc), NULL, 0, NULL, NULL);
    std::string str(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wc, wcslen(wc), &str[0], size_needed, NULL, NULL);
    return str;
}

Zyla::Zyla(std::string serial)
{

    int AT_error_code;
    DEBUG("Initialising Andor Zyla ...");
    AT_error_code = AT_InitialiseLibrary();
    check_AT_error(AT_error_code);


    DEBUG("Getting device count.");
    int num_devices = get_device_count();
    DEBUG("Detected " << num_devices << " cameras." << std::endl);


    for (int i = 0; i < num_devices; i++)
    {
        AT_error_code = AT_Open(i, &Hndl);
        this->serial_number = get_string_prop(L"SerialNumber");

        if (this->serial_number == serial)
            break;
        else
            AT_Close(Hndl);
    }

    DEBUG("Initialising Andor Utility library ...");
    AT_error_code = AT_InitialiseUtilityLibrary();
    check_AT_error(AT_error_code);


    this->serial_number = get_string_prop(L"SerialNumber");
    DEBUG("Serial number of selected camera is " << serial_number);

    DEBUG("Camera model is " << get_string_prop(L"CameraModel"));
    DEBUG("Camera name is " << get_string_prop(L"CameraName"));

    DEBUG("Setting PixelReadoutRate to 270 MHz.");
    set_enum_prop(L"PixelReadoutRate", L"270 MHz");
    std::string readout_rate = get_enum_prop(L"PixelReadoutRate");
    DEBUG("PixelReadoutRate set to " << readout_rate);

    DEBUG("Turning on sensor cooler for camera " << serial_number);
    set_bool_prop(L"SensorCooling", true);

    DEBUG("Enabling  faster framerates for small AOIs " << serial_number);
    set_bool_prop(L"FastAOIFrameRateEnable", true);
    DEBUG("FastAOI enabled: " << get_bool_prop(L"FastAOIFrameRateEnable"));

    DEBUG("Setting shutter to rolling mode.");
    set_enum_prop(L"ElectronicShutteringMode", L"Rolling");

    DEBUG("Setting Auxiliary Output to FireRow1");
    set_enum_prop(L"AuxiliaryOutSource", L"FireRow1");
    std::string auxiliary_out_source = get_enum_prop(L"AuxiliaryOutSource");
    DEBUG("Auxiliary output set to: " << auxiliary_out_source);

}

Zyla::~Zyla()
{

    DEBUG("Turning off sensor cooler.");
    set_bool_prop(L"SensorCooling", false);

    DEBUG("Closing camera.");
    check_AT_error(AT_Close(Hndl));

    DEBUG("Finalising Andor library.");
    check_AT_error(AT_FinaliseLibrary());

    DEBUG("Finalising Andor Utility library.");
    check_AT_error(AT_FinaliseUtilityLibrary());
}

void Zyla::prepare()
{

    DEBUG("Setting CycleMode to " << "Continuous" << ".");
    set_enum_prop(L"CycleMode", L"Continuous");

	DEBUG("Setting encoding to Mono16");
	set_enum_prop(L"PixelEncoding", L"Mono16");

    DEBUG("Setting overlap mode to ON ");
    set_bool_prop(L"Overlap", true);

	DEBUG("Setting PreAmp mode to 16-bit (low noise & high well capacity)");
	set_enum_prop(L"SimplePreAmpGainControl", L"16-bit (low noise & high well capacity)");

    DEBUG("Gain control set to: "
        << get_enum_prop(L"SimplePreAmpGainControl"));

    DEBUG("PixelEncoding control set to: "
        << get_enum_prop(L"PixelEncoding") << std::endl);

    command(L"AcquisitionStop");

    BufferSize = get_int_prop(L"ImageSizeBytes");

    //Allocate a number of memory buffers to store frames
    AcqBuffers = new unsigned char*[NumberOfBuffers];

	for (int i = 0; i < NumberOfBuffers; i++) 
	{ 
		AcqBuffers[i] = new unsigned char[BufferSize + 7];
	}

    //Pass these buffers to the SDK 
    int rc;
    for (int i = 0; i < NumberOfBuffers; i++)
    {
        rc = AT_QueueBuffer(Hndl, AcqBuffers[i], BufferSize);
        check_AT_error(rc);
    }

    

    Height = get_AOI_height();
    Width = get_AOI_width();
    Stride = get_AOI_stride();
    image_size = Height * Width * 2;
}

void Zyla::set_trigger_mode(int trigger_mode)
{


    switch (trigger_mode)
    {
    case 1:
        set_enum_prop(L"TriggerMode", L"Internal");
        set_exposure_time(0.05);
        set_max_framerate();
        break;
    case 2:
        set_enum_prop(L"TriggerMode", L"External Exposure");
        break;
    default:
        WARNING("Illegal trigger mode value: " << trigger_mode);
    }

}

void Zyla::requeue_buffers()
{
    AT_Flush(Hndl);
    //Pass these buffers to the SDK 
    int rc;
    for (int i = 0; i < NumberOfBuffers; i++)
    {
        DEBUG("Queueing buffer " << i);
        rc = AT_QueueBuffer(Hndl, AcqBuffers[i], BufferSize);
        check_AT_error(rc);
    }
}

void Zyla::start_continuous()
{
    requeue_buffers();
    DEBUG("Starting acquisition.");
    command(L"AcquisitionStart");
}

void Zyla::pause_continuous()
{
    DEBUG("Stopping Acquisition.");
    command(L"AcquisitionStop");
}

void Zyla::finish_continuous()
{
    command(L"AcquisitionStop");

    AT_Flush(Hndl);

    for (int i = 0; i < NumberOfBuffers; i++)
    {
        delete[] AcqBuffers[i];
    }
	delete[] AlignedBuffers;
    delete[] AcqBuffers;
}

bool Zyla::get_camera_acquiring()
{
	DEBUG("Camera Acquiring: " << get_bool_prop(L"CameraAcquiring"));
	return get_bool_prop(L"CameraAcquiring");
}

/*
void Zyla::get_image(void* output_buffer)
{
    int BufSize;
    int rc;

	rc = AT_WaitBuffer(Hndl, &pBuf, &BufSize, AT_INFINITE);
	check_AT_error(rc);


    AT_ConvertBuffer(pBuf, reinterpret_cast<AT_U8*>(output_buffer),
        Width, Height, Stride, L"Mono12Packed", L"Mono16");

    AT_QueueBuffer(Hndl, pBuf, BufferSize);
}
*/

void Zyla::get_image(unsigned char* output_buffer)
{
	int BufSize;
	int rc;

	rc = AT_WaitBuffer(Hndl, &pBuf, &BufSize, AT_INFINITE);
	check_AT_error(rc);

	AT_ConvertBuffer(pBuf, output_buffer,
		Width, Height, Stride, L"Mono16", L"Mono16");

	AT_QueueBuffer(Hndl, pBuf, BufferSize);
}


void Zyla::set_exposure_time(double seconds)
{
    set_float_prop(L"ExposureTime", seconds);
}

double Zyla::get_exposure_time()
{
    return get_float_prop(L"ExposureTime");
}

void Zyla::set_framerate(double hertz)
{
    set_float_prop(L"FrameRate", hertz);
}

void Zyla::set_max_framerate()
{
    double max_rate = get_float_max(L"FrameRate");
    set_float_prop(L"FrameRate", max_rate);
}

double Zyla::get_framerate()
{
    return get_float_prop(L"FrameRate");
}

void Zyla::set_binning(int n)
{
    std::wstring binning;
    switch (n)
    {
    case 1:
        binning = L"1x1"; break;
    case 2:
        binning = L"2x2"; break;
    case 4:
        binning = L"4x4"; break;
    case 8:
        binning = L"8x8"; break;
    default:
        WARNING("Illegal binning value: " << n);
    }
    set_enum_prop(L"AOIBinning", binning.c_str());
}

std::string Zyla::get_binning()
{
    return get_enum_prop(L"AOIBinning");
}

void Zyla::set_AOI_height(int superpixels)
{
    set_int_prop(L"AOIHeight", superpixels);
}

int Zyla::get_AOI_height()
{
    return get_int_prop(L"AOIHeight");
}

void Zyla::set_AOI_width(int superpixels)
{
    set_int_prop(L"AOIWidth", superpixels);

}

int Zyla::get_AOI_width()
{
    return get_int_prop(L"AOIWidth");
}

int Zyla::get_AOI_stride()
{
    return get_int_prop(L"AOIStride");
}

void Zyla::set_VerticallyCenterAOI(bool x)
{
    set_bool_prop(L"VerticallyCenterAOI", x);
}

bool Zyla::get_VerticallyCenterAOI()
{
    return get_bool_prop(L"VerticallyCenterAOI");
}

void Zyla::print_state()
{
    PRINT("");
    PRINT("Binning: " << get_binning());
    PRINT("AOI Height: " << get_AOI_height());
    PRINT("AOI Width: " << get_AOI_width());
    PRINT("AOI Top: " << get_int_prop(L"AOITop"));
    PRINT("AOI Left: " << get_int_prop(L"AOILeft"));
    PRINT("Exposure time: " << get_exposure_time());
    PRINT("Framerate: " << get_framerate());
    PRINT("PreAmp Mode: " << get_enum_prop(L"SimplePreAmpGainControl"));
    PRINT("Cycle Mode: " << get_enum_prop(L"CycleMode"));
    PRINT("Trigger Mode: " << get_enum_prop(L"TriggerMode"));
    PRINT("Pixel Encoding: " << get_enum_prop(L"PixelEncoding"));
    PRINT("Sensor Temperature: " << get_float_prop(L"SensorTemperature"));
    PRINT("Shuttering Mode: " << get_enum_prop(L"ElectronicShutteringMode"));
    PRINT("FastAOI enabled: " << get_bool_prop(L"FastAOIFrameRateEnable"));
    PRINT("InterfaceType: " << get_string_prop(L"InterfaceType"));
    PRINT("Overlap: " << get_bool_prop(L"Overlap"));
    PRINT("Max interface transfer rate: " << get_float_prop(L"MaxInterfaceTransferRate"));
    PRINT("");
}

int Zyla::get_device_count()
{
    AT_64 iNumberDevices = 0;
    check_AT_error(
        AT_GetInt(AT_HANDLE_SYSTEM, L"DeviceCount", &iNumberDevices));
    return iNumberDevices;
}


