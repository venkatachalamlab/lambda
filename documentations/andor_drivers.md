# Andor Technology SDK/Drives

Lambda system uses [Zyla Camera](https://andor.oxinst.com/products/scmos-camera-series/zyla-4-2-scmos), 
[Integrated Laser Engine](https://andor.oxinst.com/products/microscopy-components/integrated-laser-engine), 
and [Dragonfly 200](https://andor.oxinst.com/products/dragonfly-confocal-microscope-system) by Andor Technology.

Zyla camera and ILE are controlled by customized softwares written in cpp programming language using SDK provided by Andor technology,
and Dragonfly is controlled by sending serial commands via a python script.

### SDKs/driver location:
SDKs and Dragonfly driver are stored on 
[vendata NAS](https://github.com/venkatachalamlab/venkatachalamlab/blob/master/protocols/general/Connecting%20to%20the%20NAS.md): 
2022 > Mahdi > Andor > Drivers

## Zyla 4.2 Camera

1- Intall Andor SDK found in 'Andor Zyla Camera SDK' folder  
2- Type 'edit the system environment variables' in the task bar, and open System Properties  
3- Click on 'Environment Varibales ...' and create a new system variable which its value is where SDK is installed:  
<img src="https://user-images.githubusercontent.com/31863323/154347553-2939d3a9-b539-4539-8f15-b4adf57789a6.png" width="603" height="169" align="center"/>  
4- Open 'path' in 'system variables' and add newly created variable there:  
<img src="https://user-images.githubusercontent.com/31863323/154347255-969baa7f-02df-4729-a478-4975a3ad2ae5.png" width="486" height="527" align="center"/>  

## Integrated Laser Engine

1- Copy ALC SDK found in 'Andor ALC SDK' to a location on the computer  
2- Type 'edit the system environment variables' in the task bar, and open System Properties  
3- Click on 'Environment Varibales ...' and create a new system variable which its value is where SDK is installed:  
<img src="https://user-images.githubusercontent.com/31863323/154346776-1582816c-723b-4173-bd1e-49a7c20b11b5.png" width="603" height="169" align="center"/>  
4- Open 'path' in 'system variables' and use newly created variable to add 'Libraries' and 'Include' folder to path:  
<img src="https://user-images.githubusercontent.com/31863323/154372429-b5bb66ad-4283-4b0c-ad04-2f9131592067.png" width="486" height="527" align="center"/>  

## Dragonfly 200 Series

1- Install Andor dragonfly drive pack found in 'Andor Dragonfly Driver' folder  
2- This makes it possible to communicate with the device with serial commands
