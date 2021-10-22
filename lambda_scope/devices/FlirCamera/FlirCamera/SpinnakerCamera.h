#pragma once


// ptgrey SDK
#include "Spinnaker.h"
#include "SpinGenApi/SpinnakerGenApi.h"


class SpinnakerCamera
{
public:

	SpinnakerCamera(int SerialNumber);

	int SerialNumber;

	void set_binning(void);
	void set_width(void);
	void set_height(void);
	void set_Offset(void);
	void set_exposuretime_and_framerate(double, double);
	void begin_acquisition();
	void end_acquisition();
	void deinitialize_camera();
	void get_image(void *buffer);

	std::size_t get_image_size_bytes();
	std::string status();
	Spinnaker::ImagePtr ptrImage;

	int OffsetX = 0;
	int OffsetY = 0;
	int HorizontalBinSize = 1;
	int VerticalBinSize = 1;
	int Height = 1200;
	int Width = 1920;
	double ExposureTime = 10000.0;
	double FrameRate = (double)((int)(100 / 1.02));

	int get_device_count(void);


private:

	Spinnaker::CameraPtr ptrCamera;
	Spinnaker::SystemPtr system_;
	Spinnaker::CameraList camList_;
	void set_acquisition_mode(std::string);
	void set_frame_rate_auto(std::string);
	void set_exposure_auto(std::string);
	void set_exposure_mode(std::string);
	void print_device_info(void);



	std::string get_status();

};