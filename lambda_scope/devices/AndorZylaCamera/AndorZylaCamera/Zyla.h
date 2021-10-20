#pragma once

// Andor SDK3
#include "atcore.h"

class Zyla
{
private:

	// Most things prefixed by AT should stay private.

	AT_H Hndl;

	// State for ring buffer acquisition (SDK manual, section 5.1.4)
	int BufferSize;
	unsigned char* pBuf = NULL;
	int NumberOfBuffers = 10;
	unsigned char** AcqBuffers;
	unsigned char** AlignedBuffers;
	int BufferIdx = 0;
	int Stride;

	// Property getters and setters.

	int get_int_prop(const wchar_t* property);
	void set_int_prop(const wchar_t* property, const int &value);
	int get_int_max(const wchar_t* property);
	int get_int_min(const wchar_t* property);

	double get_float_prop(const wchar_t* property);
	void set_float_prop(const wchar_t* property, const double &value);
	double get_float_max(const wchar_t* property);
	double get_float_min(const wchar_t* property);

	std::string get_enum_prop(const wchar_t* property);
	void set_enum_prop(const wchar_t* property, const wchar_t* value);

	bool get_bool_prop(const wchar_t* property);
	void set_bool_prop(const wchar_t* property, const bool value);

	std::string get_string_prop(const wchar_t* property);
	void set_string_prop(const wchar_t* property, const wchar_t* value);



	// Error handling

	static void check_AT_error(int AT_return_code);

	// Utility

	//static const wchar_t* wchar_from_string(std::string s);
	static const std::string string_from_wchar(const wchar_t* ws);

public:
	std::string serial_number;
	int Width;
	int Height;

	Zyla(std::string serial);
	~Zyla();

	void prepare();
	void requeue_buffers();
	void start_continuous();
	void pause_continuous();
	void finish_continuous();

	size_t image_size;

	//void get_image(void* buffer, unsigned int timeout_ms);
	//void get_image(void* buffer);
	void get_image(unsigned char* buffer);

	bool get_camera_acquiring();

	void set_trigger_mode(int trigger_mode);

	void set_exposure_time(double seconds);
	double get_exposure_time();

	void command(const wchar_t* property);

	void set_framerate(double hertz);
	double get_framerate();
	void set_max_framerate();

	void set_binning(int n);
	std::string get_binning();

	void set_AOI_height(int superpixels);
	int get_AOI_height();

	void set_AOI_width(int superpixels);
	int get_AOI_width();

	int get_AOI_stride();

	void set_VerticallyCenterAOI(bool x);
	bool get_VerticallyCenterAOI();

	void print_state();

	static int get_device_count();
};

