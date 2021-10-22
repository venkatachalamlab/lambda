
#include "pch.h"

#include "SpinnakerCamera.h"
#include "macros.h"




SpinnakerCamera::SpinnakerCamera(int serialnumber)
{
	system_ = Spinnaker::System::GetInstance();
	camList_ = system_->GetCameras();


	bool camera_running = false;
	bool app_running = true;



	for (int i = 0; i < camList_.GetSize(); i++)
	{
		ptrCamera = camList_.GetByIndex(i);
		ptrCamera->Init();


		Spinnaker::GenApi::INodeMap & nodeMapTLDevice = ptrCamera->GetTLDeviceNodeMap();
		ptrCamera->BeginAcquisition();

		Spinnaker::GenICam::gcstring deviceSerialNumber("");
		Spinnaker::GenApi::CStringPtr ptrStringSerial = nodeMapTLDevice.GetNode("DeviceSerialNumber");

		if (IsAvailable(ptrStringSerial) && IsReadable(ptrStringSerial))
		{
			deviceSerialNumber = ptrStringSerial->GetValue();
		}

		if (serialnumber == atoi(deviceSerialNumber))
		{
			SerialNumber = atoi(deviceSerialNumber);
			ptrCamera->EndAcquisition();
			set_acquisition_mode("Continuous");
			set_frame_rate_auto("Off");
			set_exposure_mode("Timed");
			set_exposure_auto("Off");
			break;
		}
		else
		{
			if (i == camList_.GetSize() - 1)
			{
				std::cout << "Failed to create camera object, make sure serial number is valid." << std::endl;
				ptrCamera->EndAcquisition();
				ptrCamera->DeInit();
			}
			else
			{
				ptrCamera->EndAcquisition();
				ptrCamera->DeInit();
			}
		}
	}
}

void SpinnakerCamera::set_binning(void)
{
	try
	{
		Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
		Spinnaker::GenApi::CIntegerPtr ptrBinningHorizontal = nodeMap.GetNode("BinningHorizontal");
		Spinnaker::GenApi::CIntegerPtr ptrBinningVertical = nodeMap.GetNode("BinningVertical");

		ptrBinningVertical->SetValue(VerticalBinSize);

		HorizontalBinSize = ptrBinningHorizontal->GetValue();
		VerticalBinSize = ptrBinningVertical->GetValue();

		DEBUG("FlirCamera #" << SerialNumber << ": binning is " << VerticalBinSize << "x" << HorizontalBinSize);
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}




void SpinnakerCamera::set_width(void)
{
	try
	{
		Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
		Spinnaker::GenApi::CIntegerPtr ptrWidth = nodeMap.GetNode("Width");
		ptrWidth->SetValue(Width);
		Width = ptrWidth->GetValue();
		DEBUG("FlirCamera #" << SerialNumber << ": Width is " << Width);
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}



void SpinnakerCamera::set_height(void)
{
	try
	{
		Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
		Spinnaker::GenApi::CIntegerPtr ptrHeight = nodeMap.GetNode("Height");
		ptrHeight->SetValue(Height);
		Height = ptrHeight->GetValue();
		DEBUG("FlirCamera #" << SerialNumber << ": Height is " << Height);
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}


void SpinnakerCamera::set_Offset(void)
{
	try
	{
		Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
		Spinnaker::GenApi::CIntegerPtr ptrOffsetX = nodeMap.GetNode("OffsetX");
		Spinnaker::GenApi::CIntegerPtr ptrOffsetY = nodeMap.GetNode("OffsetY");


		OffsetY = (600 / VerticalBinSize) - (Height / 2);
		OffsetX = (960 / HorizontalBinSize) - (Width / 2);

		ptrOffsetX->SetValue(OffsetX);
		ptrOffsetY->SetValue(OffsetY);
		OffsetX = ptrOffsetX->GetValue();
		OffsetY = ptrOffsetY->GetValue();
		DEBUG("FlirCamera #" << SerialNumber << ": Offset is (" << OffsetY << "," << OffsetX << ")");
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}






void SpinnakerCamera::set_acquisition_mode(std::string acquisitionmode)
{
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
	try
	{
		Spinnaker::GenApi::CEnumerationPtr ptrAcquisitionMode = nodeMap.GetNode("AcquisitionMode");

		if (acquisitionmode == "Continuous")
		{
			ptrAcquisitionMode->SetIntValue(ptrAcquisitionMode->GetEntryByName("Continuous")->GetValue());
		}
		else if (acquisitionmode == "SingleFrame")
		{
			ptrAcquisitionMode->SetIntValue(ptrAcquisitionMode->GetEntryByName("SingleFrame")->GetValue());
		}
		else if (acquisitionmode == "MultiFrame")
		{
			ptrAcquisitionMode->SetIntValue(ptrAcquisitionMode->GetEntryByName("MultiFrame")->GetValue());
		}
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}



void SpinnakerCamera::set_frame_rate_auto(std::string framerateauto)
{
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
	try
	{
		Spinnaker::GenApi::CEnumerationPtr ptrFrameRateAuto = nodeMap.GetNode("AcquisitionFrameRateAuto");

		if (framerateauto == "Off")
		{
			ptrFrameRateAuto->SetIntValue(ptrFrameRateAuto->GetEntryByName("Off")->GetValue());
		}
		else if (framerateauto == "Continuous")
		{
			ptrFrameRateAuto->SetIntValue(ptrFrameRateAuto->GetEntryByName("Continuous")->GetValue());
		}
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}



void SpinnakerCamera::set_exposure_auto(std::string exposureauto)
{
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
	try
	{
		Spinnaker::GenApi::CEnumerationPtr ptrExposureAuto = nodeMap.GetNode("ExposureAuto");

		if (exposureauto == "Continuous")
		{
			ptrExposureAuto->SetIntValue(ptrExposureAuto->GetEntryByName("Continuous")->GetValue());
		}

		else if (exposureauto == "Once")
		{
			ptrExposureAuto->SetIntValue(ptrExposureAuto->GetEntryByName("Once")->GetValue());
		}

		else if (exposureauto == "Off")
		{
			ptrExposureAuto->SetIntValue(ptrExposureAuto->GetEntryByName("Off")->GetValue());
		}
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}



void SpinnakerCamera::set_exposure_mode(std::string exposuremode)
{
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();
	try
	{

		Spinnaker::GenApi::CEnumerationPtr ptrExposureMode = nodeMap.GetNode("ExposureMode");

		if (exposuremode == "Timed")
		{
			ptrExposureMode->SetIntValue(ptrExposureMode->GetEntryByName("Timed")->GetValue());
		}
		else if (exposuremode == "TriggerWidth")
		{
			ptrExposureMode->SetIntValue(ptrExposureMode->GetEntryByName("TriggerWidth")->GetValue());
		}
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}

void SpinnakerCamera::SpinnakerCamera::set_exposuretime_and_framerate(double exposuretime, double framerate)
{
	ptrCamera->BeginAcquisition();
	ptrCamera->EndAcquisition();
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();

	try
	{

		Spinnaker::GenApi::CFloatPtr ptrExposureTime = nodeMap.GetNode("ExposureTime");
		Spinnaker::GenApi::CFloatPtr ptrAcquisitionFrameRate = nodeMap.GetNode("AcquisitionFrameRate");

		ptrAcquisitionFrameRate->SetValue(framerate);
		FrameRate = ptrAcquisitionFrameRate->GetValue();
		DEBUG("FlirCamera #" << SerialNumber << ": Frame Rate is " << FrameRate << "(Hz)");

		ptrExposureTime->SetValue(exposuretime);
		ExposureTime = ptrExposureTime->GetValue();
		DEBUG("FlirCamera #" << SerialNumber << ": Exposure Time is " << ExposureTime << "(micro second)");

	}

	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}
}

void SpinnakerCamera::print_device_info(void)
{
	Spinnaker::GenApi::INodeMap & nodeMap = ptrCamera->GetNodeMap();

	std::cout << std::endl << "*** DEVICE INFORMATION ***" << std::endl << std::endl;
	try
	{
		Spinnaker::GenApi::FeatureList_t features;
		Spinnaker::GenApi::CCategoryPtr category = nodeMap.GetNode("DeviceInformation");
		if (IsAvailable(category) && IsReadable(category))
		{
			category->GetFeatures(features);
			Spinnaker::GenApi::FeatureList_t::const_iterator it;
			for (it = features.begin(); it != features.end(); ++it)
			{
				Spinnaker::GenApi::CNodePtr pfeatureNode = *it;
				std::cout << pfeatureNode->GetName() << " : ";
				Spinnaker::GenApi::CValuePtr pValue = (Spinnaker::GenApi::CValuePtr)pfeatureNode;
				std::cout << (IsReadable(pValue) ? pValue->ToString() : (Spinnaker::GenICam::gcstring)("Node not readable")) << std::endl;
			}
		}
		else
		{
			std::cout << "Device control information not available." << std::endl;
		}
	}
	catch (Spinnaker::Exception &e)
	{
		std::cout << "Error: " << e.what() << std::endl;
	}

}


void SpinnakerCamera::begin_acquisition()
{
	ptrCamera->BeginAcquisition();
}



void SpinnakerCamera::end_acquisition()
{
	ptrCamera->EndAcquisition();
}

void SpinnakerCamera::deinitialize_camera()
{
	ptrCamera->DeInit();
	ptrCamera = NULL;
	camList_.Clear();
	system_->ReleaseInstance();
}






std::string SpinnakerCamera::get_status()
{
	std::ostringstream s, w, h, e, sn;

	w << Width;
	h << Height;
	e << ExposureTime;
	sn << SerialNumber;

	std::string str_w, str_h, str_e, str_s, str_sn;
	str_w = w.str();
	str_h = h.str();
	str_e = e.str();
	str_sn = sn.str();

	s << "{\"camera" << str_sn << "\":{\"width\": " << str_w << ", \"height\": " << str_h << ", \"exposretime\": " << str_e << "}}";
	return s.str();
}



std::string SpinnakerCamera::status()
{
	std::ostringstream msg;

	msg << "hub " << get_status();

	return msg.str();
}

std::size_t SpinnakerCamera::get_image_size_bytes()
{

	return Height * Width;

}

void SpinnakerCamera::get_image(void *buffer)
{

	ptrImage = ptrCamera->GetNextImage();
	std::memcpy(buffer, ptrImage->GetData(), get_image_size_bytes());

}



int SpinnakerCamera::get_device_count()
{
	int numCameras = camList_.GetSize();
	return numCameras;
}






